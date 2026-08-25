import re
from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .models import Profile

TOP_N = 5
TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.]{1,}")


@dataclass
class MatchResult:
    profile: Profile
    score: float
    score_pct: int
    explanation: str
    shared_skills: list[str]
    is_gap_fit: bool = False


# Missing roles to keyword mapping for gap-aware boosting
ROLE_KEYWORDS = {
    "designer": ["ui", "ux", "design", "figma", "illustrator", "graphic", "layout", "frontend", "interface", "sketch", "product designer", "mockup", "photoshop", "wireframe"],
    "developer": ["python", "django", "developer", "backend", "frontend", "javascript", "coding", "engineer", "programming", "code", "web", "software", "database", "sql", "git", "java", "c++", "rust", "typescript", "react", "html", "css", "api"],
    "domain expert": ["domain", "expert", "finance", "healthcare", "industry", "business", "management", "strategy", "product manager", "pm", "marketing", "sales", "consulting", "founder", "operations", "legal"],
    "data/research": ["data", "research", "science", "analysis", "analytics", "machine learning", "ai", "statistics", "sql", "python", "pandas", "numpy", "r", "bi", "jupyter", "visualization", "deep learning"],
    "marketing/ops": ["marketing", "operations", "ops", "content", "social media", "seo", "growth", "sales", "support", "customer", "communication", "pr", "adwords", "copywriting", "strategy"],
}


def skill_tags(profile: Profile) -> list[str]:
    """Return non-empty, display-ready skill tags from a profile."""
    return [tag.strip() for tag in (profile.skills or "").split(",") if tag.strip()]


def display_name(profile: Profile) -> str:
    """Return a profile owner's full name, falling back to their username."""
    name = profile.user.get_full_name().strip()
    return name or profile.user.username


def initials(profile: Profile) -> str:
    """Return up to two uppercase initials for a profile owner's display name."""
    name = display_name(profile)
    parts = [p for p in name.split() if p]
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return name[:2].upper()


def _profile_text(profile: Profile) -> str:
    """Combine the text fields that form one profile's TF-IDF document."""
    return " ".join(
        part for part in (profile.skills, profile.interests, profile.looking_for) if part
    ).strip()


def _word_set(text: str) -> set[str]:
    """Normalize text into the tokens used by explanation generation."""
    return set(TOKEN_RE.findall((text or "").lower()))


def _skill_key_map(tags: list[str]) -> dict[str, str]:
    """Map lowercased skill names to their original display spelling."""
    mapping = {}
    for tag in tags:
        mapping[tag.lower()] = tag
    return mapping


def explain_match(target: Profile, other: Profile) -> tuple[str, list[str]]:
    """Build a human-readable reason and shared skills for a candidate match."""
    target_skills = skill_tags(target)
    other_skills = skill_tags(other)
    target_keys = _skill_key_map(target_skills)
    other_keys = _skill_key_map(other_skills)
    shared_keys = sorted(set(target_keys) & set(other_keys))
    shared_skills = [target_keys[k] for k in shared_keys]

    their_looking = _word_set(other.looking_for)
    your_looking = _word_set(target.looking_for)
    your_trait = next(
        (tag for tag in target_skills if tag.lower() in their_looking),
        None,
    )
    if your_trait is None:
        your_trait = next(
            (tag for tag in other_skills if tag.lower() in your_looking),
            None,
        )

    shared_interest_words = sorted(
        _word_set(target.interests) & _word_set(other.interests)
    )

    parts = []
    if shared_skills:
        listed = ", ".join(shared_skills[:4])
        parts.append(f"Strong overlap in {listed}.")
    if your_trait:
        parts.append(f"They're looking for someone with {your_trait}.")
    elif shared_interest_words:
        listed = ", ".join(shared_interest_words[:3])
        parts.append(f"You both care about {listed}.")
    elif not parts:
        parts.append(
            "Your profiles share similar language around skills, interests, and what you're looking for."
        )

    return " ".join(parts), shared_skills


def _gap_alignment(profile: Profile, missing_role: str) -> tuple[float, bool, str]:
    """Return the existing role-gap boost, flag, and explanation for a profile.

    The checks intentionally preserve the previous skills-first, interests-second,
    then-looking-for order so role-filter ranking remains unchanged.
    """
    role_key = missing_role.strip().lower()
    keywords = ROLE_KEYWORDS.get(role_key, [])
    matched_terms: list[str] = []

    for skill in skill_tags(profile):
        normalized_skill = skill.lower()
        if any(keyword == normalized_skill or keyword in normalized_skill for keyword in keywords):
            matched_terms.append(skill)

    if not matched_terms:
        for interest in (profile.interests or "").split(","):
            cleaned_interest = interest.strip()
            if not cleaned_interest:
                continue
            normalized_interest = cleaned_interest.lower()
            if any(keyword == normalized_interest or keyword in normalized_interest for keyword in keywords):
                matched_terms.append(cleaned_interest)

    if matched_terms:
        matched_summary = ", ".join(matched_terms[:3])
        return (
            0.25,
            True,
            f"Fills your {missing_role} gap — strong {matched_summary} background.",
        )

    if any(keyword in (profile.looking_for or "").lower() for keyword in keywords):
        return (
            0.15,
            True,
            f"Fills your {missing_role} gap — aligned goals and expectations.",
        )

    return 0.0, False, ""


def find_top_matches(
    target: Profile,
    limit: int = TOP_N,
    missing_role: str | None = None,
) -> list[MatchResult]:
    """Rank candidate profiles by TF-IDF cosine similarity and optional role fit.

    One vectorizer is fitted over the complete request corpus, then one cosine
    similarity operation scores every candidate. The returned results retain the
    established scoring, boosting, explanation, and ranking behavior.
    """
    others = list(
        Profile.objects.exclude(pk=target.pk)
        .select_related("user")
        .only(
            "id",
            "skills",
            "interests",
            "looking_for",
            "experience_level",
            "user__id",
            "user__username",
            "user__first_name",
            "user__last_name",
        )
    )
    if not others:
        return []

    corpus = [_profile_text(target)] + [_profile_text(p) for p in others]
    if not any(corpus):
        return []

    try:
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2),
            min_df=1,
        )
        matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        return []

    scores = cosine_similarity(matrix[0:1], matrix[1:]).flatten()
    ranked = sorted(
        zip(others, scores, strict=True),
        key=lambda item: item[1],
        reverse=True,
    )

    results: list[MatchResult] = []
    for profile, score in ranked:
        if score <= 0:
            continue
        
        explanation, shared = explain_match(target, profile)
        
        boost, is_gap_fit, gap_explanation = (
            _gap_alignment(profile, missing_role) if missing_role else (0.0, False, "")
        )
        
        final_score = float(score) + boost
        final_score_capped = min(final_score, 1.0)
        
        if gap_explanation:
            explanation = f"{gap_explanation} {explanation}"

        results.append(
            MatchResult(
                profile=profile,
                score=final_score,
                score_pct=int(round(final_score_capped * 100)),
                explanation=explanation,
                shared_skills=shared,
                is_gap_fit=is_gap_fit,
            )
        )

    # Re-rank elements by boosted score
    if missing_role:
        results.sort(key=lambda r: r.score, reverse=True)
        
    return results[:limit]
