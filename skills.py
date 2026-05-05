"""
SkillLoader — loads OpenClaw-style skills from ./skills/.

Skills are directories containing a SKILL.md file. Two tiers:
  - skills/shared/     : loaded for every agent
  - skills/<agent>/    : loaded only for that agent

Content is injected as plain text into the agent's system prompt.
"""

from pathlib import Path

SKILLS_ROOT = Path("./skills")
CAP_CHARS = 6000


class SkillLoader:
    def __init__(self):
        self._cache: dict[str, list[tuple[str, str]]] = {}
        self._load_all()

    def _load_all(self) -> None:
        """Read every skill directory and populate the cache."""
        self._cache = {}
        shared = self._load_dir(SKILLS_ROOT / "shared")

        # Discover agent-specific subdirectories (anything that isn't 'shared')
        if SKILLS_ROOT.exists():
            agent_dirs = [
                d for d in SKILLS_ROOT.iterdir()
                if d.is_dir() and d.name != "shared"
            ]
        else:
            agent_dirs = []

        for agent_dir in agent_dirs:
            agent_name = agent_dir.name.lower()
            agent_skills = self._load_dir(agent_dir)
            self._cache[agent_name] = shared + agent_skills

        # Agents with no agent-specific dir still get shared skills
        self._cache["__shared__"] = shared

        loaded_summary = {
            name: [s for s, _ in skills]
            for name, skills in self._cache.items()
        }
        print(f"[skills] Loaded: {loaded_summary}")

    def _load_dir(self, directory: Path) -> list[tuple[str, str]]:
        """Return (skill_name, content) pairs from a skill directory tier."""
        skills: list[tuple[str, str]] = []
        if not directory.exists():
            return skills

        for skill_dir in sorted(directory.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            try:
                content = skill_md.read_text(encoding="utf-8").strip()
                if content:
                    skills.append((skill_dir.name, content))
            except Exception as e:
                print(f"[skills] Warning: could not read {skill_md}: {e}")

        return skills

    def reload(self) -> str:
        """Reload all skills from disk. Returns a summary string."""
        self._load_all()
        lines = []
        for agent_name, skills in self._cache.items():
            if agent_name == "__shared__":
                continue
            names = [s for s, _ in skills]
            lines.append(f"  {agent_name}: {names}")
        shared_names = [s for s, _ in self._cache.get("__shared__", [])]
        summary = f"Skills reloaded.\nShared: {shared_names}\n" + "\n".join(lines)
        return summary

    def get(self, agent_name: str) -> str:
        """Return formatted skill content to inject into a system prompt."""
        agent_name = agent_name.lower()
        skills = self._cache.get(agent_name) or self._cache.get("__shared__", [])

        if not skills:
            return ""

        sections: list[str] = []
        total = 0
        for skill_name, content in skills:
            block = f"### {skill_name}\n{content}"
            if total + len(block) > CAP_CHARS:
                remaining = CAP_CHARS - total
                if remaining > 100:
                    block = block[:remaining] + "\n[...truncated]"
                    sections.append(block)
                break
            sections.append(block)
            total += len(block)

        if not sections:
            return ""

        return "## Skills\n\n" + "\n\n".join(sections)

    def list_skills(self, agent_name: str | None = None) -> dict[str, list[str]]:
        """Return {agent_name: [skill_name, ...]} for display purposes."""
        if agent_name:
            agent_name = agent_name.lower()
            skills = self._cache.get(agent_name) or self._cache.get("__shared__", [])
            return {agent_name: [s for s, _ in skills]}

        result: dict[str, list[str]] = {}
        for name, skills in self._cache.items():
            if name == "__shared__":
                continue
            result[name] = [s for s, _ in skills]
        if not result:
            # No agent-specific dirs — just report shared
            shared = [s for s, _ in self._cache.get("__shared__", [])]
            if shared:
                result["shared"] = shared
        return result
