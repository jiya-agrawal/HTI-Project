"""
HTI Experiment - Data Analysis Helper
Quick script to analyze collected experimental data
"""

import pandas as pd
import json
import os
from datetime import datetime


def load_data():
    """Load experimental data from CSV."""
    results_path = 'data/results.csv'
    
    if not os.path.exists(results_path):
        print("❌ No data found. Run the experiment first!")
        return None
    
    df = pd.read_csv(results_path)
    print(f"✅ Loaded {len(df)} puzzle completions from {df['participant_id'].nunique()} participants")
    return df


def basic_statistics(df):
    """Calculate basic descriptive statistics."""
    print("\n" + "="*60)
    print("📊 BASIC STATISTICS")
    print("="*60)
    
    print(f"\nTotal Participants: {df['participant_id'].nunique()}")
    print(f"Total Puzzles Completed: {len(df)}")
    print(f"Date Range: {df['start_time'].min()} to {df['end_time'].max()}")
    
    print("\n--- Completion Time (seconds) ---")
    print(f"Mean: {df['completion_time'].mean():.2f}")
    print(f"Median: {df['completion_time'].median():.2f}")
    print(f"Std Dev: {df['completion_time'].std():.2f}")
    print(f"Min: {df['completion_time'].min():.2f}")
    print(f"Max: {df['completion_time'].max():.2f}")
    
    print("\n--- Correctness Rate ---")
    print(f"Overall: {df['final_correctness'].mean()*100:.1f}%")
    
    print("\n--- Trust Scores (1-7 scale) ---")
    print(f"Mean: {df['trust_score'].mean():.2f}")
    print(f"Std Dev: {df['trust_score'].std():.2f}")
    
    print("\n--- Confidence Scores (1-7 scale) ---")
    print(f"Mean: {df['confidence_score'].mean():.2f}")
    print(f"Std Dev: {df['confidence_score'].std():.2f}")
    
    print("\n--- Awareness Scores (1-7 scale) ---")
    print(f"Mean: {df['awareness_score'].mean():.2f}")
    print(f"Std Dev: {df['awareness_score'].std():.2f}")


def loa_analysis(df):
    """Analyze differences across LOA levels."""
    print("\n" + "="*60)
    print("🤖 LEVEL OF AUTOMATION (LOA) ANALYSIS")
    print("="*60)
    
    for loa in sorted(df['loa_level'].unique()):
        loa_data = df[df['loa_level'] == loa]
        print(f"\n--- LOA {loa} ---")
        print(f"N = {len(loa_data)}")
        print(f"Avg Completion Time: {loa_data['completion_time'].mean():.2f}s")
        print(f"Correctness Rate: {loa_data['final_correctness'].mean()*100:.1f}%")
        
        if loa != 1:  # LOA 1 has no AI
            print(f"AI Acceptance Rate: {loa_data['accepted_advice'].mean()*100:.1f}%")
            print(f"Override Rate: {loa_data['overridden'].mean()*100:.1f}%")
            print(f"Avg Trust Score: {loa_data['trust_score'].mean():.2f}")
            print(f"Avg Edit Distance: {loa_data['edit_distance'].mean():.2f}")


def faulty_ai_analysis(df):
    """Compare faulty vs. non-faulty AI conditions."""
    print("\n" + "="*60)
    print("⚠️  FAULTY AI CONDITION ANALYSIS")
    print("="*60)
    
    # Filter out LOA 1 (no AI)
    df_with_ai = df[df['loa_level'] != 1]
    
    if len(df_with_ai) == 0:
        print("No AI-assisted puzzles completed yet.")
        return
    
    print(f"\n--- Non-Faulty AI ---")
    non_faulty = df_with_ai[df_with_ai['ai_faulty'] == False]
    print(f"N = {len(non_faulty)}")
    print(f"Acceptance Rate: {non_faulty['accepted_advice'].mean()*100:.1f}%")
    print(f"Override Rate: {non_faulty['overridden'].mean()*100:.1f}%")
    print(f"Correctness: {non_faulty['final_correctness'].mean()*100:.1f}%")
    print(f"Trust Score: {non_faulty['trust_score'].mean():.2f}")
    
    print(f"\n--- Faulty AI ---")
    faulty = df_with_ai[df_with_ai['ai_faulty'] == True]
    print(f"N = {len(faulty)}")
    print(f"Acceptance Rate: {faulty['accepted_advice'].mean()*100:.1f}%")
    print(f"Override Rate: {faulty['overridden'].mean()*100:.1f}%")
    print(f"Correctness: {faulty['final_correctness'].mean()*100:.1f}%")
    print(f"Trust Score: {faulty['trust_score'].mean():.2f}")
    
    if len(non_faulty) > 0 and len(faulty) > 0:
        print(f"\n--- Comparison ---")
        trust_diff = non_faulty['trust_score'].mean() - faulty['trust_score'].mean()
        accept_diff = non_faulty['accepted_advice'].mean() - faulty['accepted_advice'].mean()
        print(f"Trust Difference: {trust_diff:+.2f} (non-faulty - faulty)")
        print(f"Acceptance Difference: {accept_diff*100:+.1f}% (non-faulty - faulty)")


def interaction_analysis(df):
    """Analyze participant interactions."""
    print("\n" + "="*60)
    print("👆 INTERACTION ANALYSIS")
    print("="*60)
    
    print(f"\nAverage Interactions per Puzzle: {df['num_interactions'].mean():.2f}")
    print(f"Average Decision Latency: {df['decision_latency'].mean():.2f}s")
    
    print("\n--- By LOA ---")
    for loa in sorted(df['loa_level'].unique()):
        loa_data = df[df['loa_level'] == loa]
        print(f"LOA {loa}: {loa_data['num_interactions'].mean():.2f} interactions, "
              f"{loa_data['decision_latency'].mean():.2f}s latency")


def export_summary_report(df):
    """Export a summary report to JSON."""
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_participants": int(df['participant_id'].nunique()),
        "total_completions": len(df),
        "overall_metrics": {
            "avg_completion_time": float(df['completion_time'].mean()),
            "correctness_rate": float(df['final_correctness'].mean()),
            "avg_trust": float(df['trust_score'].mean()),
            "avg_confidence": float(df['confidence_score'].mean()),
            "avg_awareness": float(df['awareness_score'].mean())
        },
        "loa_breakdown": {}
    }
    
    for loa in sorted(df['loa_level'].unique()):
        loa_data = df[df['loa_level'] == loa]
        summary["loa_breakdown"][f"LOA_{loa}"] = {
            "n": len(loa_data),
            "avg_completion_time": float(loa_data['completion_time'].mean()),
            "correctness_rate": float(loa_data['final_correctness'].mean()),
            "avg_trust": float(loa_data['trust_score'].mean()) if loa != 1 else None
        }
    
    output_path = 'data/analysis_summary.json'
    with open(output_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Summary report exported to: {output_path}")


def main():
    """Run all analyses."""
    print("\n" + "="*60)
    print("🧠 HTI EXPERIMENT - DATA ANALYSIS")
    print("="*60)
    
    df = load_data()
    
    if df is None:
        return
    
    # Run analyses
    basic_statistics(df)
    loa_analysis(df)
    faulty_ai_analysis(df)
    interaction_analysis(df)
    export_summary_report(df)
    
    print("\n" + "="*60)
    print("✅ ANALYSIS COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Review the statistics above")
    print("2. Check data/analysis_summary.json for exportable summary")
    print("3. Use statistical software (SPSS, R, Python) for hypothesis testing")
    print("4. Visualize trends with matplotlib/seaborn")
    print("\n")


if __name__ == "__main__":
    main()
