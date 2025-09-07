from __future__ import annotations

from typing import List, Optional

from pipelex import log
from pipelex.core.memory.working_memory import WorkingMemory
from pipelex.core.stuffs.stuff_content import StructuredContent
from pipelex.tools.func_registry import func_registry
from pydantic import Field, model_validator
from typing_extensions import Self


class StructuredChangelog(StructuredContent):
    added: List[str] = Field(default_factory=list, description="New features.")
    changed: List[str] = Field(default_factory=list, description="Updates to existing behavior.")
    fixed: List[str] = Field(default_factory=list, description="Bug fixes.")
    removed: List[str] = Field(default_factory=list, description="Features removed.")
    deprecated: List[str] = Field(default_factory=list, description="Soon-to-be removed features.")
    security: List[str] = Field(default_factory=list, description="Security-related changes.")

    # --- validation ---------------------------------------------------------
    @model_validator(mode="after")
    def _at_least_one_section(self) -> Self:
        """Require at least one non-empty change section."""
        if not any(
            (
                self.added,
                self.changed,
                self.fixed,
                self.removed,
                self.deprecated,
                self.security,
            )
        ):
            log.warning("No change sections were generated in the changelog.")
        return self


class TwitterPost(StructuredContent):
    """A Twitter-optimized social media post."""

    text: str = Field(description="The main tweet text, optimized for Twitter's character limit")
    hashtags: List[str] = Field(default_factory=list, description="Relevant hashtags for the post")
    thread_posts: Optional[List[str]] = Field(default=None, description="Additional posts if text requires a thread")

    @model_validator(mode="after")
    def _validate_twitter_constraints(self) -> Self:
        """Validate Twitter-specific constraints."""
        # Check main content length (280 chars including hashtags)
        hashtag_text = " ".join(f"#{tag}" for tag in self.hashtags)
        full_content = f"{self.text} {hashtag_text}".strip()

        if len(full_content) > 280:
            log.warning(f"Twitter post content exceeds 280 characters: {len(full_content)} chars")

        return self


class LinkedInPost(StructuredContent):
    """A LinkedIn-optimized social media post."""

    text: str = Field(description="The main LinkedIn post text, professional and engaging")
    hashtags: List[str] = Field(default_factory=list, description="Professional hashtags relevant to the post")
    call_to_action: Optional[str] = Field(default=None, description="Optional call-to-action for engagement")
    time_for_optimal_engagement: Optional[str] = Field(default=None, description="Suggested time to post for best engagement")

    @model_validator(mode="after")
    def _validate_linkedin_constraints(self) -> Self:
        """Validate LinkedIn-specific constraints."""
        # LinkedIn posts can be much longer, but warn if too short or too long
        if len(self.text) < 50:
            log.warning(f"LinkedIn post might be too short for good engagement: {len(self.text)} chars")
        elif len(self.text) > 3000:
            log.warning(f"LinkedIn post is very long: {len(self.text)} chars")

        return self


class SocialMediaPosts(StructuredContent):
    """Combined social media posts for multiple platforms."""

    twitter_post: Optional[TwitterPost] = Field(default=None, description="Twitter-optimized post")
    linkedin_post: Optional[LinkedInPost] = Field(default=None, description="LinkedIn-optimized post")

    @model_validator(mode="after")
    def _at_least_one_post(self) -> Self:
        """Require at least one social media post."""
        if not self.twitter_post and not self.linkedin_post:
            log.warning("No social media posts were generated.")
        return self


def combine_social_media_posts(working_memory: WorkingMemory) -> SocialMediaPosts:
    """Combine Twitter and LinkedIn posts into a single SocialMediaPosts structure."""
    twitter_post_stuff = working_memory.get_stuff("twitter_post")
    linkedin_post_stuff = working_memory.get_stuff("linkedin_post")

    # Cast the content to the appropriate types
    twitter_post = twitter_post_stuff.content if isinstance(twitter_post_stuff.content, TwitterPost) else None
    linkedin_post = linkedin_post_stuff.content if isinstance(linkedin_post_stuff.content, LinkedInPost) else None

    return SocialMediaPosts(twitter_post=twitter_post, linkedin_post=linkedin_post)


# Register the function
func_registry.register_function(combine_social_media_posts, name="combine_social_media_posts")
