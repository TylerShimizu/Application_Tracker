from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.core.config import config
from app.db.schema import Job, JobStatus, User
from app.models.assistant import (
    AssistantIntent,
    AssistantPlan,
    AssistantResponse,
    JobQueryFilters,
)

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class AssistantUnavailableError(Exception):
    """Raised when the assistant cannot reach the configured AI provider."""


class AssistantService:
    """Translate natural language job questions into safe database queries."""

    def __init__(self, session: Session):
        self._db = session

    def answer_query(self, user: User, message: str) -> AssistantResponse:
        plan = self._create_plan_from_ai(message=message)
        jobs = self._query_jobs(user=user, filters=plan.filters)
        companies = sorted({job.company for job in jobs})

        if plan.intent == AssistantIntent.count_jobs:
            answer = f"I found {len(jobs)} matching jobs."
            return AssistantResponse(
                answer=answer,
                intent=plan.intent,
                filters=plan.filters,
                jobs=[],
                companies=[],
                count=len(jobs),
            )

        if plan.intent == AssistantIntent.list_companies:
            answer = self._companies_answer(companies=companies)
            return AssistantResponse(
                answer=answer,
                intent=plan.intent,
                filters=plan.filters,
                jobs=[],
                companies=companies,
                count=len(companies),
            )

        answer = self._jobs_answer(count=len(jobs))
        return AssistantResponse(
            answer=answer,
            intent=plan.intent,
            filters=plan.filters,
            jobs=jobs,
            companies=companies,
            count=len(jobs),
        )

    def _create_plan_from_ai(self, message: str) -> AssistantPlan:
        if not config.OPENAI_API_KEY:
            return self._create_plan_with_rules(message=message)

        if OpenAI is None:
            raise AssistantUnavailableError(
                "The openai package is not installed. Install it to use AI assistant planning."
            )

        client = OpenAI(api_key=config.OPENAI_API_KEY)
        try:
            response = client.responses.parse(
                model=config.OPENAI_MODEL,
                input=[
                    {
                        "role": "system",
                        "content": self._system_prompt(),
                    },
                    {
                        "role": "user",
                        "content": message,
                    },
                ],
                text_format=AssistantPlan,
            )
        except Exception as exc:
            raise AssistantUnavailableError("Unable to create assistant query plan.") from exc

        return response.output_parsed

    def _query_jobs(self, user: User, filters: JobQueryFilters) -> list[Job]:
        query = self._db.query(Job).filter(Job.user_id == user.id)

        if filters.status:
            query = query.filter(Job.status == filters.status)
        if filters.company:
            query = query.filter(Job.company.ilike(f"%{filters.company}%"))
        if filters.title:
            query = query.filter(Job.title.ilike(f"%{filters.title}%"))
        if filters.location:
            query = query.filter(Job.location.ilike(f"%{filters.location}%"))
        if filters.applied_within_days:
            start_date = date.today() - timedelta(days=filters.applied_within_days)
            query = query.filter(Job.date_applied >= start_date)

        return query.order_by(Job.date_applied.desc(), Job.company, Job.title).all()

    def _create_plan_with_rules(self, message: str) -> AssistantPlan:
        normalized_message = message.lower()
        filters = JobQueryFilters()

        if "not heard back" in normalized_message or "haven't heard back" in normalized_message:
            filters.status = JobStatus.applied
        elif "applied" in normalized_message:
            filters.status = JobStatus.applied
        elif "interview" in normalized_message:
            filters.status = JobStatus.interviewing
        elif "offer" in normalized_message:
            filters.status = JobStatus.offered
        elif "reject" in normalized_message:
            filters.status = JobStatus.rejected
        elif "interested" in normalized_message:
            filters.status = JobStatus.interested

        days = self._extract_last_days(normalized_message)
        if days:
            filters.applied_within_days = days

        company = self._extract_company(normalized_message)
        if company:
            filters.company = company

        if normalized_message.startswith("how many") or "how many" in normalized_message:
            intent = AssistantIntent.count_jobs
        elif "companies" in normalized_message or "company" in normalized_message:
            intent = AssistantIntent.list_companies
        else:
            intent = AssistantIntent.list_jobs

        return AssistantPlan(intent=intent, filters=filters)

    def _extract_last_days(self, message: str) -> int | None:
        words = message.replace("?", "").replace(",", "").split()
        for index, word in enumerate(words):
            if word in {"last", "past"} and index + 1 < len(words):
                try:
                    return int(words[index + 1])
                except ValueError:
                    return None
        return None

    def _extract_company(self, message: str) -> str | None:
        if "heard back from" in message:
            return None

        markers = ("from ", "at ")
        for marker in markers:
            if marker in message:
                value = message.split(marker, 1)[1].strip(" ?.,")
                if value and value not in {"yet", "them"}:
                    return value
        return None

    def _jobs_answer(self, count: int) -> str:
        if count == 1:
            return "I found 1 matching job."
        return f"I found {count} matching jobs."

    def _companies_answer(self, companies: list[str]) -> str:
        if not companies:
            return "I did not find any matching companies."
        if len(companies) == 1:
            return f"I found 1 matching company: {companies[0]}."
        return f"I found {len(companies)} matching companies."

    def _system_prompt(self) -> str:
        return """
You translate natural language questions about a user's job applications into a safe query plan.
Never write SQL. Only choose an intent and filters.

Allowed intents:
- list_jobs: return matching job records.
- count_jobs: answer how many matching jobs exist.
- list_companies: return matching company names.

Allowed statuses:
- applied: jobs the user has applied to and has not heard back from yet.
- interviewing: jobs where the user is interviewing.
- offered: jobs where the user received an offer.
- rejected: jobs where the user was rejected.
- interested: jobs the user is interested in but has not applied to.

Interpret examples:
- "which companies have I not heard back from yet" -> list_companies, status applied.
- "how many jobs have I applied to" -> count_jobs, status applied.
- "companies I applied to in the last 30 days" -> list_companies, status applied, applied_within_days 30.
- "from acme" or "at acme" -> company "acme".
""".strip()
