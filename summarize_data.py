import pandas as pd
import numpy as np

df = pd.read_csv('data/results.csv')

print('='*60)
print('HTI EXPERIMENT - DATA SUMMARY')
print('='*60)
print(f'\nTotal Records: {len(df)}')
print(f'Unique Participants: {df["participant_id"].nunique()}')
print(f'Participant IDs: {sorted(df["participant_id"].unique())}')

# Show all columns
print(f'\n\nAll Columns ({len(df.columns)} total):')
for i, col in enumerate(df.columns[:40], 1):
    print(f'{i}. {col}')

print('\n' + '='*60)
print('LOA LEVEL DISTRIBUTION')
print('='*60)
print(df['loa_level'].value_counts().sort_index())

print('\n' + '='*60)
print('PUZZLE ID DISTRIBUTION')
print('='*60)
print(df['puzzle_id'].value_counts().sort_index())

print('\n' + '='*60)
print('AI FAULTY CONDITION')
print('='*60)
print(df['ai_faulty'].value_counts())

print('\n' + '='*60)
print('COMPLETION TIME STATISTICS (seconds)')
print('='*60)
print(f'Mean: {df["completion_time"].mean():.2f}')
print(f'Median: {df["completion_time"].median():.2f}')
print(f'Std: {df["completion_time"].std():.2f}')
print(f'Min: {df["completion_time"].min():.2f}')
print(f'Max: {df["completion_time"].max():.2f}')

print('\n' + '='*60)
print('COMPLETION TIME BY LOA LEVEL')
print('='*60)
print(df.groupby('loa_level')['completion_time'].agg(['mean', 'median', 'std', 'count']))

print('\n' + '='*60)
print('INTERACTIONS BY LOA LEVEL')
print('='*60)
print(df.groupby('loa_level')['num_interactions'].agg(['mean', 'median', 'std', 'count']))

print('\n' + '='*60)
print('DECISION LATENCY BY LOA LEVEL')
print('='*60)
print(df.groupby('loa_level')['decision_latency'].agg(['mean', 'median', 'std']))

print('\n' + '='*60)
print('CORRECTNESS ANALYSIS')
print('='*60)
if 'final_correctness' in df.columns:
    print(f'Overall Correctness Rate: {df["final_correctness"].mean()*100:.1f}%')
    print('\nCorrectness by LOA Level:')
    print(df.groupby('loa_level')['final_correctness'].mean() * 100)
else:
    print('final_correctness column not found')

print('\n' + '='*60)
print('ACCEPTED ADVICE RATE (LOA 2)')
print('='*60)
if 'accepted_advice' in df.columns:
    loa2_data = df[df['loa_level'] == 2]
    print(f'Acceptance Rate: {loa2_data["accepted_advice"].mean()*100:.1f}%')
else:
    print('accepted_advice column not found')

print('\n' + '='*60)
print('OVERRIDE BEHAVIOR (LOA 3)')
print('='*60)
if 'overridden' in df.columns:
    loa3_data = df[df['loa_level'] == 3]
    print(f'Override Rate: {loa3_data["overridden"].mean()*100:.1f}%')
else:
    print('overridden column not found')

print('\n' + '='*60)
print('PERFORMANCE BY AI FAULTY CONDITION')
print('='*60)
print('\nCompletion Time:')
print(df.groupby('ai_faulty')['completion_time'].agg(['mean', 'median']))
print('\nNum Interactions:')
print(df.groupby('ai_faulty')['num_interactions'].agg(['mean', 'median']))

print('\n' + '='*60)
print('PARTICIPANT LEVEL SUMMARY')
print('='*60)
participant_summary = df.groupby('participant_id').agg({
    'completion_time': ['mean', 'std'],
    'num_interactions': 'mean',
    'puzzle_id': 'count'
}).round(2)
participant_summary.columns = ['Avg_Time', 'Std_Time', 'Avg_Interactions', 'Num_Puzzles']
print(participant_summary)

print('\n' + '='*60)
print('DATA COLLECTION TIMELINE')
print('='*60)
df['start_time'] = pd.to_datetime(df['start_time'])
print(f'First Record: {df["start_time"].min()}')
print(f'Last Record: {df["start_time"].max()}')
print(f'Duration: {df["start_time"].max() - df["start_time"].min()}')
