from datetime import datetime, timezone
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, ValidationError


class Community(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=3)
    platform: Literal["Reddit", "Discord", "Telegram", "Other"]
    url: HttpUrl
    topic_fit: int = Field(strict=True, ge=0, le=5)
    audience_fit: int = Field(strict=True, ge=0, le=5)
    activity_score: int = Field(strict=True, ge=0, le=5)
    promotion_allowed: bool | None
    evidence_url: HttpUrl
    checked_at: datetime


raw_communities = [
    {
        "name": "Demo Trading Room A",
        "platform": "Reddit",
        "url": "https://example.com/community-a",
        "topic_fit": 5,
        "audience_fit": 4,
        "activity_score": 4,
        "promotion_allowed": True,
        "evidence_url": "https://example.com/community-a/rules",
        "checked_at": datetime.now(timezone.utc),
    },
    {
        "name": "Demo Market Group B",
        "platform": "Discord",
        "url": "https://example.com/community-b",
        "topic_fit": 4,
        "audience_fit": 5,
        "activity_score": 4,
        "promotion_allowed": None,
        "evidence_url": "https://example.com/community-b/rules",
        "checked_at": datetime.now(timezone.utc),
    },
    {
        "name": "Demo Charts Channel C",
        "platform": "Telegram",
        "url": "https://example.com/community-c",
        "topic_fit": 5,
        "audience_fit": 5,
        "activity_score": 4,
        "promotion_allowed": False,
        "evidence_url": "https://example.com/community-c/rules",
        "checked_at": datetime.now(timezone.utc),
    },
]


def score_community(community: Community) -> int:
    return (
        community.topic_fit * 10
        + community.audience_fit * 7
        + community.activity_score * 3
    )


def get_promotion_status(community: Community) -> str:
    if community.promotion_allowed is True:
        return "Rules allow promotion — review source"
    if community.promotion_allowed is False:
        return "Promotion disallowed — skip"

    return "Rules unknown — manual check needed"


communities = []

for index, raw_community in enumerate(raw_communities, start=1):
    try:
        community = Community(**raw_community)
        communities.append(community)
    except ValidationError as error:
        print(f"Community #{index} reject hui:")
        for issue in error.errors():
            print(" -", issue["loc"], issue["msg"])


ranked_communities = sorted(
    communities,
    key=lambda community: (
        community.promotion_allowed is False,
        community.promotion_allowed is None,
        -score_community(community),
    ),
)

for rank, community in enumerate(ranked_communities, start=1):
    score = score_community(community)

    print(f"\n{rank}. {community.name} — {score}/100")
    print(f"   Platform: {community.platform}")
    print(f"   Status: {get_promotion_status(community)}")
    print(
        f"   Scores: topic={community.topic_fit}/5, "
        f"audience={community.audience_fit}/5, "
        f"activity={community.activity_score}/5"
    )
    print(f"   Evidence: {community.evidence_url}")


invalid_record = {
    **raw_communities[0],
    "topic_fit": 8,
}

try:
    Community(**invalid_record)
except ValidationError as error:
    print("\nValidation check: invalid score reject hua.")
    print(error.errors()[0]["msg"])
