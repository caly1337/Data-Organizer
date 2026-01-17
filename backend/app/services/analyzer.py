"""
Analyzer Service
Uses LLM to analyze filesystem scans and generate recommendations
"""
import logging
import json
from typing import Dict, Any, List, Optional
from app.services.llm_service import llm_service

logger = logging.getLogger(__name__)


class FilesystemAnalyzer:
    """Analyzes filesystem scans using LLM"""

    def __init__(self):
        self.llm = llm_service

    async def analyze_scan(
        self,
        scan_data: Dict[str, Any],
        provider: str = "ollama",
        mode: str = "fast"
    ) -> Dict[str, Any]:
        """
        Analyze scan results and generate recommendations

        Args:
            scan_data: Scan results from FileScanner
            provider: LLM provider to use
            mode: Analysis mode (fast, deep, comparison)

        Returns:
            Analysis results with recommendations
        """

        # Build analysis prompt
        prompt = self._build_analysis_prompt(scan_data, mode)
        system_prompt = self._build_system_prompt(mode)

        # Generate analysis
        logger.info(f"Analyzing scan with {provider} in {mode} mode")
        result = await self.llm.generate(
            prompt=prompt,
            provider=provider,
            system_prompt=system_prompt
        )

        # Parse recommendations from response
        recommendations = self._parse_recommendations(result["response"], scan_data)

        return {
            "provider": result["provider"],
            "model": result["model"],
            "response": result["response"],
            "recommendations": recommendations,
            "tokens_used": result["tokens_used"],
            "cost": result["cost"],
            "duration": result["duration"],
            "metadata": result["metadata"]
        }

    async def compare_analyses(
        self,
        scan_data: Dict[str, Any],
        providers: List[str],
        mode: str = "deep"
    ) -> List[Dict[str, Any]]:
        """
        Run analysis across multiple providers for comparison

        Args:
            scan_data: Scan results
            providers: List of provider names
            mode: Analysis mode

        Returns:
            List of analysis results from each provider
        """
        results = []

        for provider in providers:
            try:
                analysis = await self.analyze_scan(scan_data, provider, mode)
                results.append(analysis)
            except Exception as e:
                logger.error(f"Analysis failed for {provider}: {e}")
                results.append({
                    "provider": provider,
                    "error": str(e)
                })

        return results

    def _build_system_prompt(self, mode: str) -> str:
        """Build system prompt for LLM"""

        base_prompt = """You are an expert filesystem analyst and organizer. Your role is to analyze filesystem scans and provide intelligent recommendations for optimization.

Your responsibilities:
1. Identify organizational inefficiencies
2. Detect duplicate files and bloat
3. Suggest logical restructuring strategies
4. Recommend cleanup opportunities
5. Prioritize suggestions by impact

Guidelines:
- Be specific and actionable
- Provide clear reasoning
- Consider user safety (never suggest destructive operations without strong justification)
- Focus on practical improvements
- Consider file relationships and dependencies

Output Format:
Provide your analysis in a structured format with:
1. Summary: High-level findings (2-3 sentences)
2. Issues: List of problems identified
3. Recommendations: Specific actions with reasoning and confidence scores (0.0-1.0)
4. Insights: Additional observations about the filesystem"""

        if mode == "deep":
            base_prompt += """

Deep Mode Guidelines:
- Perform comprehensive analysis of all file types
- Consider semantic relationships between files
- Analyze naming patterns and conventions
- Identify obsolete or deprecated files
- Suggest advanced organizational strategies
- Research file type best practices"""

        elif mode == "fast":
            base_prompt += """

Fast Mode Guidelines:
- Focus on obvious issues and quick wins
- Prioritize high-impact, low-effort changes
- Identify clear duplicates and bloat
- Suggest simple reorganization strategies"""

        return base_prompt

    def _build_analysis_prompt(self, scan_data: Dict[str, Any], mode: str) -> str:
        """Build analysis prompt from scan data"""

        # Summarize scan data
        total_files = scan_data.get("total_files", 0)
        total_dirs = scan_data.get("total_directories", 0)
        total_size = scan_data.get("total_size", 0)
        files = scan_data.get("files", [])

        # Category breakdown
        categories = {}
        for file in files:
            cat = file.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1

        # Extension breakdown
        extensions = {}
        for file in files:
            ext = file.get("extension", "none")
            extensions[ext] = extensions.get(ext, 0) + 1

        # Size analysis
        size_ranges = {
            "tiny (<10KB)": 0,
            "small (10KB-100KB)": 0,
            "medium (100KB-1MB)": 0,
            "large (1MB-10MB)": 0,
            "huge (>10MB)": 0
        }

        for file in files:
            size = file.get("size", 0)
            if size < 10 * 1024:
                size_ranges["tiny (<10KB)"] += 1
            elif size < 100 * 1024:
                size_ranges["small (10KB-100KB)"] += 1
            elif size < 1024 * 1024:
                size_ranges["medium (100KB-1MB)"] += 1
            elif size < 10 * 1024 * 1024:
                size_ranges["large (1MB-10MB)"] += 1
            else:
                size_ranges["huge (>10MB)"] += 1

        # Build prompt
        prompt = f"""Analyze the following filesystem scan and provide optimization recommendations.

**Scan Overview:**
- Path: {scan_data.get('path', 'unknown')}
- Total Files: {total_files:,}
- Total Directories: {total_dirs:,}
- Total Size: {self._format_size(total_size)}
- Scan Duration: {scan_data.get('duration', 0):.2f}s

**File Categories:**
{self._format_dict(categories, sort_by_value=True)}

**File Extensions (Top 20):**
{self._format_dict(dict(sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:20]), sort_by_value=True)}

**File Size Distribution:**
{self._format_dict(size_ranges)}

**Sample File Paths (First 50):**
"""
        # Add sample file paths
        for file in files[:50]:
            prompt += f"\n- {file.get('path', 'unknown')} ({file.get('category', 'other')}, {self._format_size(file.get('size', 0))})"

        if mode == "deep":
            prompt += "\n\n**Deep Analysis Required:**"
            prompt += "\nPerform comprehensive analysis including:"
            prompt += "\n1. Identify duplicate files by content similarity"
            prompt += "\n2. Detect obsolete or deprecated file types"
            prompt += "\n3. Analyze naming conventions and suggest improvements"
            prompt += "\n4. Recommend advanced organizational strategies"
            prompt += "\n5. Identify opportunities for archival or deletion"

        prompt += "\n\nProvide your analysis and recommendations."

        return prompt

    def _parse_recommendations(
        self,
        llm_response: str,
        scan_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Parse recommendations from LLM response"""

        # Simple parsing - in production, this would be more sophisticated
        recommendations = []

        # Look for common recommendation patterns
        lines = llm_response.split('\n')

        current_rec = None
        for line in lines:
            line = line.strip()

            # Look for recommendation markers
            if any(marker in line.lower() for marker in ['recommendation:', 'suggest:', 'action:']):
                if current_rec:
                    recommendations.append(current_rec)

                current_rec = {
                    "title": line,
                    "description": "",
                    "type": "reorganize",
                    "confidence": 0.7,
                    "reasoning": "",
                    "affected_files": [],
                    "priority": 5
                }

            elif current_rec and line:
                current_rec["description"] += line + " "

        if current_rec:
            recommendations.append(current_rec)

        # If no structured recommendations found, create a general one
        if not recommendations:
            recommendations.append({
                "title": "General Filesystem Review",
                "description": llm_response[:500],
                "type": "categorize",
                "confidence": 0.5,
                "reasoning": "LLM provided general analysis without specific recommendations",
                "affected_files": [],
                "priority": 3
            })

        return recommendations

    def _format_size(self, size_bytes: int) -> str:
        """Format size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def _format_dict(self, data: Dict[str, int], sort_by_value: bool = False) -> str:
        """Format dictionary for display"""
        if sort_by_value:
            items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        else:
            items = data.items()

        result = []
        for key, value in items:
            if isinstance(value, int):
                result.append(f"  - {key}: {value:,}")
            else:
                result.append(f"  - {key}: {value}")

        return '\n'.join(result) if result else "  (none)"


# Global analyzer instance
filesystem_analyzer = FilesystemAnalyzer()
