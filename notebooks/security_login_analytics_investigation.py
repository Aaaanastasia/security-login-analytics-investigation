import json
import warnings
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import FancyBboxPatch

warnings.filterwarnings("ignore", category=UserWarning)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ROOT = PROJECT_ROOT / "analysis_outputs"
CHART_DIR = ROOT / "charts"
CHART_DIR.mkdir(parents=True, exist_ok=True)

DATA_PATH = PROJECT_ROOT / "data" / "logins_db_for_assignment.xlsx"

COLORS = {
    "blue": "#356bc4",
    "blue_light": "#b0cdff",
    "red": "#cc4343",
    "red_light": "#f5beb8",
    "green": "#248f5d",
    "green_light": "#b8e6cd",
    "amber": "#cf8e2d",
    "muted": "#5c6370",
    "grid": "#E5E7EB",
    "ink": "#212529",
    "navy": "#0F1E46",
    "orange": "#F59E0B",
    "purple": "#9333EA",
    "gray_text": "#64748B",
    "card_border": "#E5E7EB",
    "card_bg": "#FFFFFF",
}

PALETTE = {
    "safe": "#2ecc71",
    "warn": "#e67e22",
    "danger": "#e74c3c",
    "neutral": "#95a5a6",
    "blue": "#3498db",
}

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#343a40",
        "axes.labelcolor": "#212529",
        "xtick.color": "#495057",
        "ytick.color": "#495057",
        "grid.color": "#dee2e6",
        "font.size": 11,
        "font.family": "DejaVu Sans",
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)


def save_fig(fig, filename, dpi=190):
    out = CHART_DIR / filename
    fig.savefig(out, bbox_inches="tight", facecolor="white", dpi=dpi)
    plt.close(fig)
    return str(out)


def draw_card(fig, x, y, w, h, title, value, subtitle, color):
    card = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.012,rounding_size=0.012",
        linewidth=1,
        edgecolor=COLORS["card_border"],
        facecolor=COLORS["card_bg"],
        transform=fig.transFigure,
        zorder=1,
    )
    fig.patches.append(card)
    fig.text(x + 0.025, y + h - 0.035, title, fontsize=12, color=COLORS["gray_text"])
    fig.text(x + 0.025, y + h - 0.073, value, fontsize=20, weight="bold", color=color)
    fig.text(x + 0.025, y + 0.024, subtitle, fontsize=11, color=COLORS["gray_text"])


def prep_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Expected assignment workbook at {DATA_PATH}. "
            "Copy the provided Excel file to data/logins_db_for_assignment.xlsx "
            "before running the analysis."
        )
    df = pd.read_excel(DATA_PATH)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df["successful_login"] = df["successful_login"].astype("Float64")
    df["login_result"] = df["successful_login"].fillna(0).astype(int)
    df["date"] = df["datetime"].dt.normalize()
    df["hour"] = df["datetime"].dt.hour
    df["is_failure"] = df["login_result"].eq(0)
    df["is_success"] = df["login_result"].eq(1)
    df["is_off_hours"] = ~df["hour"].between(8, 18)
    df["is_weekend"] = df["datetime"].dt.dayofweek >= 5
    return df


def chart_overview(df):
    fig, axes = plt.subplots(1, 3, figsize=(14, 4))
    outcome = (
        df["successful_login"]
        .map({1.0: "Success", 0.0: "Failure"})
        .value_counts()
    )
    axes[0].pie(
        outcome,
        labels=outcome.index,
        autopct="%1.1f%%",
        colors=[PALETTE["safe"], PALETTE["danger"]],
        startangle=90,
    )
    axes[0].set_title("Login Outcomes")

    daily = df.groupby("date").size()
    axes[1].bar(daily.index, daily.values, color=PALETTE["blue"], width=0.8)
    axes[1].set_title("Daily Login Volume")
    axes[1].set_xlabel("Date")
    axes[1].tick_params(axis="x", rotation=45)
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

    hourly = df.groupby("hour").size()
    axes[2].bar(hourly.index, hourly.values, color=PALETTE["neutral"])
    axes[2].set_title("Logins by Hour of Day")
    axes[2].set_xlabel("Hour")
    axes[2].set_xticks(range(0, 24, 2))
    fig.tight_layout()
    return save_fig(fig, "overview.png")


def chart_daily_baseline(df):
    daily = (
        df.groupby("date")
        .agg(
            attempts=("user", "size"),
            failures=("is_failure", "sum"),
            successes=("is_success", "sum"),
        )
        .reset_index()
    )
    daily["failure_rate"] = daily["failures"] / daily["attempts"] * 100

    total_attempts = int(daily["attempts"].sum())
    total_failures = int(daily["failures"].sum())
    overall_failure_rate = total_failures / total_attempts * 100
    avg_attempts = daily["attempts"].mean()
    avg_failures = daily["failures"].mean()
    avg_daily_failure_rate = daily["failure_rate"].mean()

    spike_date = pd.Timestamp("2024-02-09")
    spike = daily.loc[daily["date"].eq(spike_date)].iloc[0]

    fig = plt.figure(figsize=(18, 10), facecolor="white")
    fig.text(
        0.04,
        0.94,
        "Daily Login Attempts and Failures",
        fontsize=24,
        weight="bold",
        color=COLORS["navy"],
    )
    card_y = 0.79
    card_h = 0.105
    card_w = 0.205
    gap = 0.025
    x0 = 0.04
    draw_card(
        fig,
        x0,
        card_y,
        card_w,
        card_h,
        "Total Attempts",
        f"{total_attempts:,}",
        f"Avg / day: {avg_attempts:.0f}",
        COLORS["blue"],
    )
    draw_card(
        fig,
        x0 + (card_w + gap),
        card_y,
        card_w,
        card_h,
        "Total Failures",
        f"{total_failures:,}",
        f"Avg / day: {avg_failures:.1f}",
        COLORS["red"],
    )
    draw_card(
        fig,
        x0 + 2 * (card_w + gap),
        card_y,
        card_w,
        card_h,
        "Failure Rate",
        f"{overall_failure_rate:.2f}%",
        f"Avg daily rate: {avg_daily_failure_rate:.2f}%",
        COLORS["orange"],
    )
    draw_card(
        fig,
        x0 + 3 * (card_w + gap),
        card_y,
        card_w,
        card_h,
        "Date Range",
        f"{daily['date'].min():%b %d} - {daily['date'].max():%b %d, %Y}",
        f"{daily['date'].nunique()} days",
        COLORS["purple"],
    )

    ax = fig.add_axes([0.08, 0.16, 0.82, 0.54])
    ax2 = ax.twinx()
    ax.bar(
        daily["date"],
        daily["attempts"],
        color=COLORS["blue_light"],
        label="Attempts",
        width=0.85,
        alpha=0.9,
    )
    ax.bar(
        daily["date"],
        daily["failures"],
        color=COLORS["red"],
        label="Failures",
        width=0.85,
        alpha=0.9,
    )
    ax2.plot(
        daily["date"],
        daily["failure_rate"],
        color=COLORS["navy"],
        marker="o",
        markersize=4,
        linewidth=2,
        label="Failure Rate (%)",
    )
    ax.axvline(spike["date"], color=COLORS["red"], linestyle="--", linewidth=1.5, alpha=0.5)
    ax.annotate(
        f"2024-02-09\n{int(spike['failures'])} failures / {int(spike['attempts'])} attempts\nFailure rate: {spike['failure_rate']:.1f}%",
        xy=(spike["date"], spike["attempts"]),
        xytext=(spike["date"] + pd.Timedelta(days=5), spike["attempts"] + 35),
        arrowprops=dict(arrowstyle="-|>", color=COLORS["red"], lw=2),
        bbox=dict(boxstyle="round,pad=0.5", fc="#FFF5F5", ec=COLORS["red"], alpha=0.95),
        color=COLORS["red"],
        fontsize=12,
        weight="bold",
        ha="center",
    )
    ax.set_ylabel("Count", fontsize=13, color=COLORS["blue"], weight="bold")
    ax2.set_ylabel("Failure Rate (%)", fontsize=13, color=COLORS["red"], weight="bold")
    ax.tick_params(axis="y", colors=COLORS["blue"])
    ax2.tick_params(axis="y", colors=COLORS["red"])
    ax.grid(axis="y", color=COLORS["grid"], linewidth=1)
    ax.set_axisbelow(True)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    ax.set_ylim(0, max(daily["attempts"]) * 1.25)
    ax2.set_ylim(0, max(daily["failure_rate"]) * 1.25)
    handles1, labels1 = ax.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    fig.legend(
        handles1 + handles2,
        labels1 + labels2,
        loc="upper left",
        bbox_to_anchor=(0.08, 0.735),
        ncol=3,
        frameon=False,
        fontsize=12,
    )
    return save_fig(fig, "baseline_daily_attempts_failures.png"), daily


def chart_anomaly1(df):
    u97 = df[df["user"] == "user_097"].copy()
    u97["failed"] = u97["is_failure"].astype(int)
    daily_fails = u97.groupby("date")["failed"].sum().reset_index()

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = [
        PALETTE["danger"] if pd.Timestamp(d) == pd.Timestamp("2024-02-09") else PALETTE["warn"]
        for d in daily_fails["date"]
    ]
    axes[0].bar(daily_fails["date"], daily_fails["failed"], color=colors, width=0.8)
    axes[0].set_title("user_097 - Daily Failed Logins", fontweight="bold")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("Failed Attempts")
    axes[0].xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    axes[0].tick_params(axis="x", rotation=45)
    axes[0].annotate(
        "Burst: 48 fails\nat same second",
        xy=(pd.Timestamp("2024-02-09"), 48),
        xytext=(pd.Timestamp("2024-02-15"), 40),
        arrowprops=dict(arrowstyle="->", color="black"),
        fontsize=9,
        color="darkred",
    )

    top_ips = u97["ip"].value_counts().head(10).index
    ip_stats = (
        u97[u97["ip"].isin(top_ips)]
        .groupby("ip")["failed"]
        .agg(["sum", "count"])
        .rename(columns={"sum": "Failures", "count": "Total"})
    )
    ip_stats["Successes"] = ip_stats["Total"] - ip_stats["Failures"]
    ip_stats = ip_stats.sort_values("Failures", ascending=True)
    axes[1].barh(ip_stats.index, ip_stats["Failures"], color=PALETTE["danger"], label="Failures")
    axes[1].barh(
        ip_stats.index,
        ip_stats["Successes"],
        left=ip_stats["Failures"],
        color=PALETTE["safe"],
        label="Successes",
    )
    axes[1].set_title("user_097 - Top 10 IPs: Success vs Failure", fontweight="bold")
    axes[1].set_xlabel("Login Count")
    axes[1].legend()
    fig.tight_layout()
    path_a = save_fig(fig, "anomaly1_brute_force.png")

    case1 = df[
        (df["user"].eq("user_097"))
        & (df["ip"].eq("103.56.23.138"))
        & (df["datetime"].between("2024-02-09 18:24:00", "2024-02-09 18:24:01"))
    ].copy()
    per_second = (
        case1.groupby("datetime")
        .agg(failures=("is_failure", "sum"), successes=("is_success", "sum"), attempts=("user", "size"))
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    x = np.arange(len(per_second))
    ax.bar(x, per_second["failures"], color=COLORS["red"], label="Failures")
    ax.bar(x, per_second["successes"], bottom=per_second["failures"], color=COLORS["green"], label="Successes")
    ax.set_xticks(x)
    ax.set_xticklabels(per_second["datetime"].dt.strftime("%H:%M:%S"))
    ax.set_ylabel("Attempts")
    ax.set_title("user_097: 93 attempts from one IP in two seconds", fontsize=16, weight="bold", loc="left")
    for i, row in per_second.iterrows():
        ax.text(i, row["attempts"] + 1, f"{int(row['attempts'])} attempts", ha="center", weight="bold")
    ax.legend(frameon=False)
    path_b = save_fig(fig, "user097_two_second_burst.png")
    return path_a, path_b


def chart_anomaly2(df):
    u3 = df[df["user"] == "user_003"].copy()
    u3["date_str"] = u3["datetime"].dt.strftime("%m-%d")
    u3["failed"] = u3["is_failure"].astype(int)
    u3_fails = u3[u3["failed"] == 1].copy()
    pivot = u3.pivot_table(index="hour", columns="date_str", values="failed", aggfunc="sum").fillna(0)

    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    sns.heatmap(pivot, ax=axes[0], cmap="Reds", linewidths=0.3, cbar_kws={"label": "Failed Logins"})
    axes[0].set_title("user_003 - Failed Logins by Hour x Date", fontweight="bold")
    axes[0].set_xlabel("Date (MM-DD)")
    axes[0].set_ylabel("Hour of Day")
    axes[0].tick_params(axis="x", rotation=90, labelsize=7)

    nightly = u3_fails[u3_fails["ip"] == "142.147.67.230"]
    other_fails = u3_fails[u3_fails["ip"] != "142.147.67.230"]
    axes[1].scatter(other_fails["datetime"], other_fails["hour"], c=PALETTE["warn"], s=40, label="Other failures", alpha=0.7)
    axes[1].scatter(
        nightly["datetime"],
        nightly["hour"],
        c=PALETTE["danger"],
        s=60,
        marker="x",
        linewidths=2,
        label=f"Nightly probe (142.147.67.230) - {len(nightly)} events",
    )
    axes[1].axhline(20, color="red", linestyle="--", linewidth=1, alpha=0.5, label="20:00 line")
    axes[1].set_title("user_003 - All Failed Logins Timeline", fontweight="bold")
    axes[1].set_xlabel("Date")
    axes[1].set_ylabel("Hour of Day")
    axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    axes[1].legend(fontsize=8)
    axes[1].tick_params(axis="x", rotation=45)
    fig.tight_layout()
    path_a = save_fig(fig, "anomaly2_nightly_probe.png")

    case2 = df[(df["user"].eq("user_003")) & (df["ip"].eq("142.147.67.230"))].sort_values("datetime").copy()
    fig, ax = plt.subplots(figsize=(14, 3.6))
    colors = case2["login_result"].map({0: COLORS["red"], 1: COLORS["green"]}).fillna(COLORS["amber"])
    ax.scatter(case2["datetime"], np.ones(len(case2)), s=180, marker="s", color=colors)
    ax.set_yticks([])
    ax.set_title("user_003: one 20:00 attempt per day; 32 failures then success", fontsize=16, weight="bold", loc="left")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.grid(axis="x", alpha=0.6)
    ax.scatter([], [], s=120, marker="s", color=COLORS["red"], label="Failed login")
    ax.scatter([], [], s=120, marker="s", color=COLORS["green"], label="Successful login")
    ax.legend(frameon=False, loc="upper left")
    path_b = save_fig(fig, "user003_low_and_slow.png")
    return path_a, path_b


def chart_anomaly3(df):
    shared_ip = "45.139.113.61"
    event = df[df["ip"] == shared_ip].copy()
    event["failed"] = event["is_failure"].astype(int)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    event_sorted = event.sort_values("login_result", ascending=False)
    bar_colors = [PALETTE["safe"] if s == 1 else PALETTE["danger"] for s in event_sorted["login_result"]]
    axes[0].barh(event_sorted["user"], [1] * len(event_sorted), color=bar_colors)
    axes[0].set_title(f"20 users from IP {shared_ip}\nat identical timestamp 2024-03-14 12:05:00", fontweight="bold")
    axes[0].set_xlabel("Login attempt (1 per user)")
    axes[0].legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, fc=PALETTE["safe"], label="Success"),
            plt.Rectangle((0, 0), 1, 1, fc=PALETTE["danger"], label="Failure"),
        ],
        loc="lower right",
    )

    ip_user_count = df.groupby("ip")["user"].nunique().sort_values(ascending=False).head(15)
    bar_c2 = [PALETTE["danger"] if ip == shared_ip else PALETTE["neutral"] for ip in ip_user_count.index]
    axes[1].bar(range(len(ip_user_count)), ip_user_count.values, color=bar_c2)
    axes[1].set_xticks(range(len(ip_user_count)))
    axes[1].set_xticklabels(ip_user_count.index, rotation=45, ha="right", fontsize=8)
    axes[1].set_title("Top IPs by Unique User Count", fontweight="bold")
    axes[1].set_ylabel("Distinct Users")
    axes[1].annotate("Anomaly IP", xy=(0, 20), xytext=(3, 18), arrowprops=dict(arrowstyle="->"), fontsize=9, color="darkred")
    fig.tight_layout()
    path_a = save_fig(fig, "anomaly3_shared_ip.png")

    case3 = df[df["ip"].eq(shared_ip)].sort_values(["login_result", "user"], ascending=[False, True]).copy()
    fig, ax = plt.subplots(figsize=(12, 6))
    y = np.arange(len(case3))
    bar_colors = case3["login_result"].map({1: COLORS["green_light"], 0: COLORS["red_light"]}).fillna(COLORS["amber"])
    edge_colors = case3["login_result"].map({1: COLORS["green"], 0: COLORS["red"]}).fillna(COLORS["amber"])
    ax.barh(y, np.ones(len(case3)), color=bar_colors, edgecolor=edge_colors, linewidth=2)
    ax.set_yticks(y)
    ax.set_yticklabels(case3["user"])
    ax.set_xticks([])
    ax.invert_yaxis()
    ax.set_title("IP 45.139.113.61: 20 users at the exact same timestamp", fontsize=16, weight="bold", loc="left")
    for idx, row in enumerate(case3.itertuples()):
        label = "success" if row.login_result == 1 else "failed"
        color = COLORS["green"] if row.login_result == 1 else COLORS["red"]
        ax.text(0.04, idx, label, va="center", color=color, weight="bold")
    path_b = save_fig(fig, "ip45_multi_user_spray.png")
    return path_a, path_b


def chart_anomaly4(df):
    user_stats = (
        df.groupby("user")
        .agg(total=("user", "count"), unique_ips=("ip", "nunique"), failures=("is_failure", "sum"))
        .reset_index()
    )
    user_stats["fail_rate"] = user_stats["failures"] / user_stats["total"]
    user_stats["ip_velocity"] = user_stats["unique_ips"] / user_stats["total"]
    user_stats["suspicion_score"] = user_stats["failures"] * user_stats["ip_velocity"]
    flagged = user_stats[(user_stats["ip_velocity"] > 0.6) | (user_stats["fail_rate"] > 0.3)]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    normal = user_stats[~user_stats["user"].isin(flagged["user"])]
    axes[0].scatter(normal["ip_velocity"], normal["fail_rate"], c=PALETTE["blue"], s=50, alpha=0.6, label="Normal")
    axes[0].scatter(flagged["ip_velocity"], flagged["fail_rate"], c=PALETTE["danger"], s=100, zorder=5, label="Flagged")
    for _, row in flagged.iterrows():
        axes[0].annotate(row["user"], (row["ip_velocity"], row["fail_rate"]), fontsize=7, ha="left", color="darkred")
    axes[0].axvline(0.6, color="orange", linestyle="--", linewidth=1, label="Threshold 0.6")
    axes[0].axhline(0.3, color="red", linestyle="--", linewidth=1, label="Threshold 0.3")
    axes[0].set_xlabel("IP Velocity (unique IPs / total logins)")
    axes[0].set_ylabel("Failure Rate")
    axes[0].set_title("User Risk Matrix - IP Velocity vs Failure Rate", fontweight="bold")
    axes[0].legend(fontsize=8)

    top15 = user_stats.nlargest(15, "unique_ips")
    bar_c = [PALETTE["danger"] if u in flagged["user"].values else PALETTE["blue"] for u in top15["user"]]
    axes[1].barh(top15["user"], top15["unique_ips"], color=bar_c)
    axes[1].set_title("Top 15 Users by Unique IP Count", fontweight="bold")
    axes[1].set_xlabel("Unique IPs")
    fig.tight_layout()
    return save_fig(fig, "anomaly4_ip_velocity.png"), user_stats, flagged


def chart_anomaly5(df):
    heatmap_data = df.groupby(["user", "hour"]).size().unstack(fill_value=0)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    sns.heatmap(heatmap_data, ax=axes[0], cmap="Blues", linewidths=0.1, xticklabels=range(24), yticklabels=True, cbar_kws={"label": "Login Count"})
    axes[0].set_title("All Users - Login Count by Hour of Day", fontweight="bold")
    axes[0].set_xlabel("Hour of Day")
    axes[0].set_ylabel("User")
    axes[0].tick_params(axis="y", labelsize=6)
    axes[0].axvspan(0, 5, alpha=0.15, color="red", label="Off-hours (00-05)")

    hourly_total = df.groupby("hour").size()
    bar_cols = [PALETTE["danger"] if h < 6 else PALETTE["blue"] for h in hourly_total.index]
    axes[1].bar(hourly_total.index, hourly_total.values, color=bar_cols, width=0.8)
    axes[1].set_title("Total Logins by Hour - Off-Hours Highlighted", fontweight="bold")
    axes[1].set_xlabel("Hour of Day")
    axes[1].set_ylabel("Login Count")
    axes[1].set_xticks(range(0, 24))
    axes[1].legend(
        handles=[
            plt.Rectangle((0, 0), 1, 1, fc=PALETTE["danger"], label="Off-hours (00-05)"),
            plt.Rectangle((0, 0), 1, 1, fc=PALETTE["blue"], label="Business hours"),
        ]
    )
    fig.tight_layout()
    return save_fig(fig, "anomaly5_offhours.png")


def chart_log_integrity(df):
    quality_counts = pd.Series(
        {
            "Missing IP": int(df["ip"].isna().sum()),
            "Missing device_type": int(df["device_type"].isna().sum()),
            "Missing network_type": int(df["network_type"].isna().sum()),
            "Missing successful_login": int(df["successful_login"].isna().sum()),
            "Non-standard device label": int(df["device_type"].eq("desktop computer").sum()),
            "Non-standard network label": int(df["network_type"].eq("home wifi").sum()),
        }
    )
    fig, ax = plt.subplots(figsize=(11, 4.8))
    quality_counts.sort_values().plot(kind="barh", ax=ax, color=COLORS["amber"])
    ax.set_title("Log integrity issues", fontsize=16, weight="bold", loc="left")
    ax.set_xlabel("Rows")
    for i, value in enumerate(quality_counts.sort_values()):
        ax.text(value + 0.05, i, int(value), va="center", weight="bold")
    return save_fig(fig, "log_integrity_issues.png"), quality_counts


def chart_signup_dashboard():
    np.random.seed(12)
    dates = pd.date_range("2024-01-01", periods=90, freq="D")
    base = 120
    trend = np.linspace(0, 20, 90)
    noise = np.random.normal(0, 15, 90)
    surge = np.zeros(90)
    surge[83:] = np.array([60, 80, 190, 220, 210, 200, 195])
    signups = np.maximum(0, base + trend + noise + surge).astype(int)
    verified = (signups * np.clip(np.random.normal(0.78, 0.05, 90), 0.5, 1.0)).astype(int)
    activated = (verified * np.clip(np.random.normal(0.55, 0.08, 90), 0.3, 0.8)).astype(int)
    paid_pct = np.clip(np.random.normal(0.30, 0.04, 90), 0.1, 0.6)
    paid_pct[83:] = np.clip(paid_pct[83:] * 0.6, 0.1, 0.6)
    organic = (signups * np.clip(np.random.normal(0.40, 0.05, 90), 0.2, 0.7)).astype(int)
    paid_ch = (signups * np.clip(np.random.normal(0.25, 0.04, 90), 0.1, 0.5)).astype(int)
    referral = (signups * np.clip(np.random.normal(0.20, 0.04, 90), 0.05, 0.4)).astype(int)
    direct = np.maximum(0, signups - organic - paid_ch - referral)
    geo_labels = ["US", "EU", "APAC", "LATAM", "Other"]
    geo_pre = [40, 25, 18, 10, 7]
    geo_surge = [30, 18, 12, 8, 32]
    df_kpi = pd.DataFrame(
        {
            "date": dates,
            "signups": signups,
            "verified": verified,
            "activated": activated,
            "paid_pct": paid_pct,
            "organic": organic,
            "paid": paid_ch,
            "referral": referral,
            "direct": direct,
        }
    )
    df_kpi["verify_rate"] = df_kpi["verified"] / df_kpi["signups"]
    df_kpi["activate_rate"] = df_kpi["activated"] / df_kpi["verified"].replace(0, np.nan)
    df_kpi["7d_avg"] = df_kpi["signups"].rolling(7).mean()
    surge_start = pd.Timestamp("2024-03-25")

    fig, axes = plt.subplots(3, 2, figsize=(16, 12))
    fig.suptitle("New Customer Sign-Ups - KPI Monitoring Dashboard", fontsize=18, weight="bold", y=0.98)
    fig.text(0.5, 0.945, "Red shading = surge period (Mar 25+) | Quality drop-off during spike", ha="center", fontsize=11, color="#495057")

    bar_colors = ["#e74c3c" if d >= surge_start else "#3498db" for d in df_kpi.date]
    axes[0, 0].bar(df_kpi.date, df_kpi.signups, color=bar_colors, label="Daily sign-ups")
    axes[0, 0].plot(df_kpi.date, df_kpi["7d_avg"], color="#f39c12", linewidth=2, label="7-day avg")
    axes[0, 0].axvspan(surge_start, df_kpi.date.max(), color="#e74c3c", alpha=0.08)
    axes[0, 0].set_title("Daily Sign-ups with 7-Day Rolling Avg")
    axes[0, 0].legend(frameon=False, fontsize=8)

    bottoms = np.zeros(len(df_kpi))
    for ch, col in [("organic", "#3498db"), ("paid", "#e74c3c"), ("referral", "#2ecc71"), ("direct", "#95a5a6")]:
        axes[0, 1].bar(df_kpi.date, df_kpi[ch], bottom=bottoms, color=col, label=ch.capitalize())
        bottoms += df_kpi[ch].values
    axes[0, 1].set_title("Acquisition Channel Mix")
    axes[0, 1].legend(frameon=False, fontsize=8, ncol=2)

    axes[1, 0].plot(df_kpi.date, df_kpi.verify_rate, color="#3498db", linewidth=2, label="Email verify rate")
    axes[1, 0].plot(df_kpi.date, df_kpi.activate_rate, color="#2ecc71", linewidth=2, label="Activation rate")
    axes[1, 0].axvspan(surge_start, df_kpi.date.max(), color="#e74c3c", alpha=0.08)
    axes[1, 0].set_title("Funnel Conversion Rates")
    axes[1, 0].legend(frameon=False, fontsize=8)
    axes[1, 0].set_ylim(0, 1)

    x = np.arange(len(geo_labels))
    axes[1, 1].bar(x - 0.18, geo_pre, width=0.36, color="#3498db", label="Pre-surge %")
    axes[1, 1].bar(x + 0.18, geo_surge, width=0.36, color="#e74c3c", label="Surge week %")
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(geo_labels)
    axes[1, 1].set_title("Geographic Distribution: Pre-Surge vs Surge Week")
    axes[1, 1].legend(frameon=False, fontsize=8)

    axes[2, 0].plot(df_kpi.date, df_kpi.verify_rate.rolling(7).mean(), color="#3498db", linewidth=2, label="Verify rate (7d)")
    axes[2, 0].plot(df_kpi.date, df_kpi.activate_rate.rolling(7).mean(), color="#2ecc71", linewidth=2, label="Activate rate (7d)")
    axes[2, 0].axvspan(surge_start, df_kpi.date.max(), color="#e74c3c", alpha=0.08)
    axes[2, 0].set_title("Account Quality Rates (7d rolling)")
    axes[2, 0].set_ylim(0, 1)
    axes[2, 0].legend(frameon=False, fontsize=8)

    axes[2, 1].fill_between(df_kpi.date, df_kpi.paid_pct, color="rgba" if False else "#e74c3c", alpha=0.2)
    axes[2, 1].plot(df_kpi.date, df_kpi.paid_pct, color="#e74c3c", linewidth=1.5)
    axes[2, 1].axvspan(surge_start, df_kpi.date.max(), color="#e74c3c", alpha=0.08)
    axes[2, 1].set_title("Paid Conversion Rate (quality proxy)")
    axes[2, 1].set_ylim(0, 0.45)

    for ax in axes.flat:
        ax.grid(axis="y", alpha=0.25)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.tick_params(axis="x", rotation=45, labelsize=8)

    fig.tight_layout(rect=[0, 0, 1, 0.93])
    return save_fig(fig, "signup_kpi_dashboard.png")


def main():
    df = prep_data()
    chart_paths = {}
    chart_paths["overview"] = chart_overview(df)
    chart_paths["baseline_daily_attempts_failures"], daily = chart_daily_baseline(df)
    chart_paths["anomaly1_brute_force"], chart_paths["user097_two_second_burst"] = chart_anomaly1(df)
    chart_paths["anomaly2_nightly_probe"], chart_paths["user003_low_and_slow"] = chart_anomaly2(df)
    chart_paths["anomaly3_shared_ip"], chart_paths["ip45_multi_user_spray"] = chart_anomaly3(df)
    chart_paths["anomaly4_ip_velocity"], user_stats, flagged = chart_anomaly4(df)
    chart_paths["anomaly5_offhours"] = chart_anomaly5(df)
    chart_paths["log_integrity_issues"], quality_counts = chart_log_integrity(df)
    chart_paths["signup_kpi_dashboard"] = chart_signup_dashboard()

    feb9 = daily.loc[daily["date"].eq(pd.Timestamp("2024-02-09"))].iloc[0]
    user97 = df[df["user"].eq("user_097")]
    burst = df[(df["user"].eq("user_097")) & (df["datetime"].eq(pd.Timestamp("2024-02-09 18:24:00")))]
    user003_probe = df[(df["user"].eq("user_003")) & (df["ip"].eq("142.147.67.230"))]
    shared = df[df["ip"].eq("45.139.113.61")]
    offhours = df[df["hour"] < 6]
    user009_offhours = offhours[offhours["user"].eq("user_009")]

    summary = {
        "data_path": str(DATA_PATH),
        "chart_paths": chart_paths,
        "shape": [int(df.shape[0]), int(df.shape[1])],
        "date_min": df["datetime"].min().strftime("%Y-%m-%d"),
        "date_max": df["datetime"].max().strftime("%Y-%m-%d"),
        "unique_users": int(df["user"].nunique()),
        "total_attempts": int(len(df)),
        "successes": int(df["is_success"].sum()),
        "failures": int(df["is_failure"].sum()),
        "failure_rate": float(df["is_failure"].mean()),
        "duplicates": int(df.duplicated().sum()),
        "missing": {k: int(v) for k, v in df[["datetime", "user", "ip", "device_type", "network_type", "successful_login"]].isna().sum().items()},
        "quality_counts": {k: int(v) for k, v in quality_counts.items()},
        "feb9_spike": {
            "date": "2024-02-09",
            "attempts": int(feb9["attempts"]),
            "failures": int(feb9["failures"]),
            "failure_rate": float(feb9["failure_rate"]),
        },
        "user097": {
            "total_attempts": int(len(user97)),
            "failures": int(user97["is_failure"].sum()),
            "failure_rate": float(user97["is_failure"].mean()),
            "unique_ips": int(user97["ip"].nunique()),
            "burst_same_second_attempts": int(len(burst)),
            "burst_ip": "103.56.23.138",
            "burst_timestamp": "2024-02-09 18:24:00",
        },
        "user003": {
            "probe_attempts": int(len(user003_probe)),
            "probe_failures": int(user003_probe["is_failure"].sum()),
            "probe_successes": int(user003_probe["is_success"].sum()),
            "probe_ip": "142.147.67.230",
            "first_seen": user003_probe["datetime"].min().strftime("%Y-%m-%d %H:%M:%S"),
            "last_seen": user003_probe["datetime"].max().strftime("%Y-%m-%d %H:%M:%S"),
            "unique_ips": int(df[df["user"].eq("user_003")]["ip"].nunique()),
        },
        "shared_ip": {
            "ip": "45.139.113.61",
            "attempts": int(len(shared)),
            "distinct_users": int(shared["user"].nunique()),
            "failures": int(shared["is_failure"].sum()),
            "successes": int(shared["is_success"].sum()),
            "timestamp": shared["datetime"].min().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "risk_matrix": {
            "flagged_users": int(len(flagged)),
            "top_by_suspicion": user_stats.sort_values("suspicion_score", ascending=False)
            .head(8)[["user", "total", "unique_ips", "failures", "fail_rate", "ip_velocity", "suspicion_score"]]
            .round(3)
            .to_dict(orient="records"),
        },
        "offhours": {
            "total_logins_00_05": int(len(offhours)),
            "user009_logins_00_05": int(len(user009_offhours)),
            "user009_unique_ips": int(df[df["user"].eq("user_009")]["ip"].nunique()),
        },
    }

    out_json = ROOT / "notebook_visual_summary.json"
    out_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    source_notes = ROOT / "source_notes.txt"
    source_notes.write_text(
        "\n".join(
            [
                "Sources used for deck content and analytical visuals:",
                "- Assignment brief: summarized in docs/task_explanation.md",
                f"- Login workbook: {DATA_PATH}",
                "- Original Colab export: notebooks/original_colab_export.py",
                "- Analytical charts were generated from the notebook transformations and chart definitions.",
                "- Colab-only upload code and notebook-state issues were corrected for local batch execution.",
                "- KPI dashboard uses the notebook's synthetic KPI generation logic with a fixed seed for reproducible export.",
            ]
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
