#!/usr/bin/env python
"""Analyze res/ Excel files. All output in English to avoid terminal encoding issues."""
import pandas as pd

# ============================================================
# Data 1: Timesheet
# Cols: 0=project,1=person,2=dept,3=creator,4=date,5=hours,6=description
# ============================================================
print("=" * 60)
print("[Data1] 2026-01-01~2026-06-30 timesheet.xlsx")
print("=" * 60)

xls1 = "D:/work_space/agent-driven_gen/docs/res/2026-01-01~2026-06-30工时明细.xlsx"
df1 = pd.read_excel(xls1, "Sheet1")
df1.columns = ["project", "person", "dept", "creator", "date", "hours", "desc"]

df1["date"] = pd.to_datetime(df1["date"])
df1["month"] = df1["date"].dt.to_period("M")

N = len(df1)
print(f"Rows: {N}")
print(f"Projects: {df1['project'].nunique()}")
print(f"Persons: {df1['person'].nunique()}")
print(f"Date range: {df1['date'].min().date()} ~ {df1['date'].max().date()}")
print(f"Total hours: {df1['hours'].sum():.1f}h")
print(f"Avg hours/person: {df1['hours'].sum() / df1['person'].nunique():.1f}h")
print(f"Avg hours/day: {df1['hours'].sum() / df1['date'].nunique():.1f}h")

print("\n--- By Project (top 20) ---")
pj = df1.groupby("project")["hours"].agg(["sum","count","mean"]).sort_values("sum", ascending=False)
pj.columns = ["total_h","records","avg_h"]
for idx, row in pj.head(20).iterrows():
    n = int(row["records"])
    print(f"  {idx[:50]:<52s} | {row['total_h']:>8.1f}h | {n:>5d} entries | avg {row['avg_h']:.2f}h")

print("\n--- By Month ---")
mo = df1.groupby("month")["hours"].agg(["sum","count"]).sort_index()
mo.columns = ["total_h","records"]
for idx, row in mo.iterrows():
    n = int(row["records"])
    print(f"  {idx} | {row['total_h']:>8.1f}h | {n:>5d} entries")

print("\n--- By Dept (top 15) ---")
dp = df1.groupby("dept")["hours"].agg(["sum","count"]).sort_values("sum", ascending=False)
dp.columns = ["total_h","records"]
for idx, row in dp.head(15).iterrows():
    n = int(row["records"])
    print(f"  {str(idx)[:35]:<37s} | {row['total_h']:>8.1f}h | {n:>5d} entries")

print("\n--- By Person (top 15) ---")
pp = df1.groupby("person")["hours"].sum().sort_values(ascending=False)
for i, (name, h) in enumerate(pp.head(15).items()):
    print(f"  {i+1:>2}. {name:<12s} {h:>8.1f}h")

print("\n--- Per-person monthly hours (sample 5 persons) ---")
top5_names = pp.head(5).index.tolist()
ppm = df1[df1["person"].isin(top5_names)].groupby(["person","month"])["hours"].sum().unstack(fill_value=0)
print(ppm.to_string())

# ============================================================
# Data 2: Roster
# ============================================================
print("\n\n" + "=" * 60)
print("[Data2] Roster.xlsx")
print("=" * 60)

xls2 = "D:/work_space/agent-driven_gen/docs/res/完整花名册_合并整理.xlsx"
df2 = pd.read_excel(xls2, "完整花名册")
df2 = df2.iloc[:, :21]
df2.columns = [
    "name","emp_id","position","dept1","dept2","dept3","dept4",
    "actual_group","role","plan_proj1","plan_proj2","plan_proj3","plan_proj4","plan_proj5",
    "remark","person_type","emp_status","position_name","hire_date","leave_date","temp_note"
]

print(f"Rows: {len(df2)}")
print(f"Null emp_id: {df2['emp_id'].isna().sum()}/{len(df2)}")

print("\n--- emp_status ---")
print(df2["emp_status"].value_counts().to_string())

print("\n--- position_name (top 10) ---")
print(df2["position_name"].value_counts().head(10).to_string())

print("\n--- dept1 ---")
print(df2["dept1"].value_counts().to_string())

print("\n--- dept2 ---")
print(df2["dept2"].value_counts().to_string())

print("\n--- role ---")
print(df2["role"].value_counts().to_string())

print("\n--- person_type ---")
print(df2["person_type"].value_counts().to_string())

# ============================================================
# Cross analysis
# ============================================================
print("\n\n" + "=" * 60)
print("[Cross] Roster vs Timesheet")
print("=" * 60)

roster_names = set(df2["name"].dropna().str.strip())
timesheet_names = set(df1["person"].dropna().str.strip())
both = roster_names & timesheet_names
only_roster = roster_names - timesheet_names
only_ts = timesheet_names - roster_names

print(f"Roster persons: {len(roster_names)}")
print(f"Timesheet persons: {len(timesheet_names)}")
print(f"Both: {len(both)}")
print(f"Only roster (no hours): {len(only_roster)}")
print(f"Only timesheet: {len(only_ts)}")
if only_ts:
    print(f"  Names: {sorted(only_ts)}")

# Merge: person -> role + total hours
print("\n--- Per-person: name + role + dept2 + total_hours (top 20) ---")
person_hours = df1.groupby("person")["hours"].sum()
merged = df2[["name","role","position_name","dept2","emp_status"]].copy()
merged["total_hours"] = merged["name"].map(person_hours)
merged = merged.sort_values("total_hours", ascending=False)
print(merged.head(20).to_string())

print("\n--- By Role: total hours ---")
role_hours = merged.groupby("role")["total_hours"].agg(["sum","count","mean"]).sort_values("sum", ascending=False)
for idx, row in role_hours.iterrows():
    n = int(row["count"])
    print(f"  {str(idx):<20s} | {row['sum']:>8.1f}h | {n:>3d} persons | avg {row['mean']:.1f}h")

# Active employees with hours
active = merged[(merged["emp_status"].isin(["正式","正式(在编)","在编"])) & merged["total_hours"].notna()]
print(f"\nActive employees with hours: {len(active)} persons, total {active['total_hours'].sum():.1f}h, avg {active['total_hours'].mean():.1f}h/person")

# By dept2 (from roster) + hours
print("\n--- By dept2 + total hours ---")
dept2_hours = merged.groupby("dept2")["total_hours"].agg(["sum","count","mean"]).sort_values("sum", ascending=False)
for idx, row in dept2_hours.iterrows():
    n = int(row["count"])
    print(f"  {str(idx)[:30]:<32s} | {row['sum']:>8.1f}h | {n:>3d} persons | avg {row['mean']:.1f}h")

# Hours distribution
print("\n--- Hours distribution ---")
bins = [0, 20, 50, 100, 150, 200, 300, 500]
labels = ["0-20","20-50","50-100","100-150","150-200","200-300","300+"]
merged["hours_bucket"] = pd.cut(merged["total_hours"], bins=bins, labels=labels, right=False)
print(merged["hours_bucket"].value_counts().sort_index().to_string())
