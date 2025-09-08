#!/bin/bash

# Hackathon Repository Analysis Script using GNU Parallel
# Usage: ./analyze_hackathon_repos.sh [repos_file] [parallel_jobs] [output_dir]

set -e  # Exit on any error

# Default values
REPOS_FILE="${1:-repos.txt}"
PARALLEL_JOBS="${2:-4}"
OUTPUT_DIR="${3:-results}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PATH="$SCRIPT_DIR/.venv"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

echo_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

echo_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if we're in the right directory
check_environment() {
    if [[ ! -f "pyproject.toml" ]] || [[ ! -d ".venv" ]]; then
        echo_error "This script must be run from the project root directory with a .venv folder"
        exit 1
    fi
    
    if [[ ! -f "$REPOS_FILE" ]]; then
        echo_error "Repository list file '$REPOS_FILE' not found!"
        echo_info "Create a text file with one repository path/URL per line"
        echo_info "Example content:"
        echo "  https://github.com/user/repo1"
        echo "  /path/to/local/repo2"
        echo "  user/repo3"
        exit 1
    fi
    
    # Check if virtual environment exists and has cocode
    if [[ ! -f "$VENV_PATH/bin/python" ]]; then
        echo_error "Virtual environment not found at $VENV_PATH"
        exit 1
    fi
    
    # Test if cocode is available in venv
    if ! "$VENV_PATH/bin/cocode" --help > /dev/null 2>&1; then
        echo_error "cocode command not available in virtual environment"
        echo_info "Make sure you've installed the project: pip install -e ."
        exit 1
    fi
}

# Function to analyze a single repository
analyze_repo() {
    local repo="$1"
    local output_dir="$2"
    local venv_path="$3"
    
    echo_info "Analyzing: $repo"
    
    # Use the virtual environment's cocode binary
    if "$venv_path/bin/cocode" hackathon analyze "$repo" -o "$output_dir"; then
        echo_success "Completed: $repo"
        return 0
    else
        echo_error "Failed: $repo"
        return 1
    fi
}

# Export the function so parallel can use it
export -f analyze_repo
export -f echo_info
export -f echo_success
export -f echo_error

# Main execution
main() {
    echo_info "Starting Hackathon Repository Analysis"
    echo_info "Repository list: $REPOS_FILE"
    echo_info "Parallel jobs: $PARALLEL_JOBS"
    echo_info "Output directory: $OUTPUT_DIR"
    echo ""
    
    # Check environment
    check_environment
    
    # Count repositories
    REPO_COUNT=$(wc -l < "$REPOS_FILE" | tr -d ' ')
    echo_info "Found $REPO_COUNT repositories to analyze"
    
    # Create output directory
    mkdir -p "$OUTPUT_DIR"
    
    # Create log directory
    LOG_DIR="$OUTPUT_DIR/logs"
    mkdir -p "$LOG_DIR"
    
    echo_info "Starting parallel analysis..."
    echo_warning "This may take a while depending on repository sizes and complexity"
    echo ""
    
    # Use GNU Parallel to process repositories
    # --progress: Show progress bar
    # --joblog: Log job execution details
    # --results: Store stdout/stderr for each job
    # --halt: Continue on errors but report them
    # -j: Number of parallel jobs
    if parallel \
        --progress \
        --joblog "$LOG_DIR/parallel_jobs.log" \
        --results "$LOG_DIR/job_outputs" \
        --halt never \
        -j "$PARALLEL_JOBS" \
        analyze_repo {} "$OUTPUT_DIR" "$VENV_PATH" :::: "$REPOS_FILE"; then
        
        echo ""
        echo_success "Parallel analysis completed!"
    else
        echo ""
        echo_warning "Parallel analysis completed with some failures"
    fi
    
    # Summary
    echo ""
    echo_info "=== ANALYSIS SUMMARY ==="
    
    # Count successful vs failed jobs from the joblog
    if [[ -f "$LOG_DIR/parallel_jobs.log" ]]; then
        SUCCESSFUL=$(awk 'NR>1 && $7==0 {count++} END {print count+0}' "$LOG_DIR/parallel_jobs.log")
        FAILED=$(awk 'NR>1 && $7!=0 {count++} END {print count+0}' "$LOG_DIR/parallel_jobs.log")
        
        echo_info "Total repositories: $REPO_COUNT"
        echo_success "Successful analyses: $SUCCESSFUL"
        if [[ $FAILED -gt 0 ]]; then
            echo_error "Failed analyses: $FAILED"
            
            # Extract and display failed repository names
            FAILED_REPOS=$(awk 'NR>1 && $7!=0 {print $9}' "$LOG_DIR/parallel_jobs.log")
            if [[ -n "$FAILED_REPOS" ]]; then
                echo_error "Failed repositories:"
                while IFS= read -r repo; do
                    echo_error "  - $repo"
                done <<< "$FAILED_REPOS"
            fi
            
            echo_info "Check detailed logs: grep -v '^1' '$LOG_DIR/parallel_jobs.log' | awk '\$7!=0 {print \$9}'"
        fi
    fi
    
    echo_info "Results saved to: $OUTPUT_DIR"
    echo_info "Job logs saved to: $LOG_DIR"
    echo ""
    echo_info "To retry failed jobs, you can extract failed repo paths and create a new input file:"
    echo_info "awk 'NR>1 && \$7!=0 {print \$9}' '$LOG_DIR/parallel_jobs.log' > failed_repos.txt"
}

# Show usage if --help is passed
if [[ "$1" == "--help" ]] || [[ "$1" == "-h" ]]; then
    echo "Usage: $0 [repos_file] [parallel_jobs] [output_dir]"
    echo ""
    echo "Arguments:"
    echo "  repos_file     Path to text file containing repository paths/URLs (default: repos.txt)"
    echo "  parallel_jobs  Number of parallel analysis jobs to run (default: 4)"
    echo "  output_dir     Directory to save analysis results (default: results)"
    echo ""
    echo "Examples:"
    echo "  $0                                    # Use defaults"
    echo "  $0 my_repos.txt 8 hackathon_results  # Custom settings"
    echo ""
    echo "The repos file should contain one repository per line:"
    echo "  https://github.com/user/repo1"
    echo "  /path/to/local/repo2"
    echo "  user/repo3"
    exit 0
fi

# Run main function
main "$@"
