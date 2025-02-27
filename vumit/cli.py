import click
from rich.console import Console
from rich.panel import Panel
from .git_analyzer import GitAnalyzer
from .ai_service import AIService

console = Console()

@click.group()
def cli():
    """Vumit - AI-powered Git analysis tool"""
    pass

@cli.command()
@click.option('--target', default='dev', help='Target branch to compare against (default: dev)')
def check(target):
    """Check feature branch commits and get AI recommendations"""
    try:
        git_analyzer = GitAnalyzer()
        ai_service = AIService()

        with console.status("Analyzing branch commits..."):
            commits = git_analyzer.get_branch_commits(target_branch=target)
            if not commits:
                console.print("[yellow]No commits found to analyze[/yellow]")
                return

        with console.status("Getting AI recommendations..."):
            analysis = ai_service.analyze_commits(commits)

        # Display results
        console.print(Panel.fit(
            analysis["summary"],
            title="Code Analysis Summary",
            border_style="blue"
        ))

        if analysis.get("issues"):
            console.print("\n[bold red]Potential Issues:[/bold red]")
            for issue in analysis["issues"]:
                console.print(f"• {issue}")

        if analysis.get("recommendations"):
            console.print("\n[bold green]Recommendations:[/bold green]")
            for rec in analysis["recommendations"]:
                console.print(f"• {rec}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

@cli.command()
@click.option('--target', default='dev', help='Target branch to compare against (default: dev)')
def report(target):
    """Generate merge request description based on branch commits"""
    try:
        git_analyzer = GitAnalyzer()
        ai_service = AIService()

        with console.status("Analyzing repository context..."):
            context = git_analyzer.get_repository_context()
            commits = git_analyzer.get_branch_commits(target_branch=target)

            if not commits:
                console.print("[yellow]No commits found to generate report[/yellow]")
                return

        with console.status("Generating merge request description..."):
            report = ai_service.generate_mr_description(commits, context)

        # Display results in sections
        console.print("\n[bold blue]Merge Request Description[/bold blue]")

        # Section 1: What does this MR do and why?
        console.print("\n[bold]1. What does this MR do and why?[/bold]")
        console.print(report["purpose"])

        if report.get("changes_explanation"):
            console.print("\nKey Changes:")
            for change in report["changes_explanation"]:
                console.print(f"• {change}")

        if report.get("problems_solved"):
            console.print("\nProblems Solved:")
            for problem in report["problems_solved"]:
                console.print(f"• {problem}")

        # Section 2: References
        console.print("\n[bold]2. References[/bold]")
        references = report.get("references", {})
        if references.get("jira_tickets"):
            console.print("\nJira Tickets:")
            for ticket in references["jira_tickets"]:
                console.print(f"• {ticket}")

        if references.get("related_mrs"):
            console.print("\nRelated MRs:")
            for mr in references["related_mrs"]:
                console.print(f"• {mr}")

        if references.get("documentation"):
            console.print("\nDocumentation Updates:")
            for doc in references["documentation"]:
                console.print(f"• {doc}")

        # MR Acceptance Checklist
        console.print("\n[bold]MR Acceptance Checklist[/bold]")
        if report.get("acceptance_checklist"):
            for item in report["acceptance_checklist"]:
                console.print(f"☐ {item}")

        # Section 3: How to set up and validate locally
        console.print("\n[bold]3. How to set up and validate locally[/bold]")
        if report.get("setup_steps"):
            console.print("\nSetup Steps:")
            for step in report["setup_steps"]:
                console.print(f"• {step}")

        if report.get("validation_steps"):
            console.print("\nValidation Steps:")
            for step in report["validation_steps"]:
                console.print(f"• {step}")

        if report.get("side_effects"):
            console.print("\nPotential Side Effects:")
            for effect in report["side_effects"]:
                console.print(f"⚠ {effect}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")

def main():
    cli()

if __name__ == "__main__":
    main()