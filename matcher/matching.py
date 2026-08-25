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
    return [tag.strip() for tag in (profile.skills or "").split(",") if tag.strip()]


def display_name(profile: Profile) -> str:
    name = profile.user.get_full_name().strip()
    return name or profile.user.username


def initials(profile: Profile) -> str:
    name = display_name(profile)
    parts = [p for p in name.split() if p]
    if len(parts) >= 2:
        return f"{parts[0][0]}{parts[1][0]}".upper()
    return name[:2].upper()


def _profile_text(profile: Profile) -> str:
    return " ".join(
        part for part in (profile.skills, profile.interests, profile.looking_for) if part
    ).strip()


def _word_set(text: str) -> set[str]:
    return set(TOKEN_RE.findall((text or "").lower()))


def _skill_key_map(tags: list[str]) -> dict[str, str]:
    mapping = {}
    for tag in tags:
        mapping[tag.lower()] = tag
    return mapping


def explain_match(target: Profile, other: Profile) -> tuple[str, list[str]]:
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


def find_top_matches(target: Profile, limit: int = TOP_N, missing_role: str = None) -> list[MatchResult]:
    others = list(
        Profile.objects.exclude(pk=target.pk).select_related("user")
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
        
        # Check gap alignment
        is_gap_fit = False
        boost = 0.0
        gap_explanation = ""
        
        if missing_role:
            role_key = missing_role.strip().lower()
            keywords = ROLE_KEYWORDS.get(role_key, [])
            matched_terms = []
            
            # Check skills
            for s in (profile.skills or "").split(","):
                s_clean = s.strip()
                if not s_clean:
                    continue
                s_low = s_clean.lower()
                if any(kw == s_low or kw in s_low for kw in keywords):
                    matched_terms.append(s_clean)
            
            # Check interests
            if not matched_terms:
                for i in (profile.interests or "").split(","):
                    i_clean = i.strip()
                    if not i_clean:
                        continue
                    i_low = i_clean.lower()
                    if any(kw == i_low or kw in i_low for kw in keywords):
                        matched_terms.append(i_clean)
            
            if matched_terms:
                is_gap_fit = True
                boost = 0.25
                skills_str = ", ".join(matched_terms[:3])
                gap_explanation = f"Fills your {missing_role} gap — strong {skills_str} background."
            elif any(kw in (profile.looking_for or "").lower() for kw in keywords):
                is_gap_fit = True
                boost = 0.15
                gap_explanation = f"Fills your {missing_role} gap — aligned goals and expectations."
        
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

