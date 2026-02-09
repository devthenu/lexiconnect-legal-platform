import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { listAuditLogs } from "../../features/admin/services/auditLogs.service";
import "./AuditLogCalendar.css";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const PAGE_SIZE_MONTH = 200;
const PAGE_SIZE_DAY = 200;

const pad = (n) => String(n).padStart(2, "0");

const toDateKey = (date) => {
  const year = date.getFullYear();
  const month = pad(date.getMonth() + 1);
  const day = pad(date.getDate());
  return `${year}-${month}-${day}`;
};

const getEntryDate = (entry) => {
  const raw = entry?.occurred_at || entry?.created_at;
  if (!raw) return null;
  const d = new Date(raw);
  if (Number.isNaN(d.getTime())) return null;
  return d;
};

const formatActor = (entry) => {
  const role = entry.actor_role || entry?.meta?.actor_role;
  const base = entry.actor_email || (entry.actor_user_id ? `#${entry.actor_user_id}` : "-");
  return role ? `${base} (${role})` : base;
};

const formatEntity = (entry) => {
  const entityType = entry.entity_type || entry?.meta?.entity_type;
  const entityId = entry.entity_id || entry?.meta?.entity_id;
  if (!entityType && !entityId) return "-";
  return `${entityType || "entity"}${entityId ? `:${entityId}` : ""}`;
};

const formatTime = (entry) => {
  const d = getEntryDate(entry);
  if (!d) return "-";
  return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
};

const formatApiError = (err) => {
  const detail = err?.response?.data?.detail;
  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const loc = Array.isArray(item?.loc) ? item.loc.join(".") : "error";
        const msg = item?.msg || "Invalid request";
        return `${loc}: ${msg}`;
      })
      .join(" | ");
  }
  if (detail && typeof detail === "object") {
    try {
      return JSON.stringify(detail);
    } catch {
      return "Request failed.";
    }
  }
  return detail || err?.message || "Request failed.";
};

export default function AuditLogCalendar() {
  const navigate = useNavigate();
  const [currentMonth, setCurrentMonth] = useState(() => {
    const now = new Date();
    return new Date(now.getFullYear(), now.getMonth(), 1);
  });
  const [monthCache, setMonthCache] = useState({});
  const [monthLoading, setMonthLoading] = useState(false);
  const [monthError, setMonthError] = useState("");
  const [selectedDate, setSelectedDate] = useState("");
  const [dayItems, setDayItems] = useState({});
  const [dayLoading, setDayLoading] = useState(false);
  const [dayError, setDayError] = useState("");

  const monthKey = useMemo(() => {
    const year = currentMonth.getFullYear();
    const month = pad(currentMonth.getMonth() + 1);
    return `${year}-${month}`;
  }, [currentMonth]);

  const monthLabel = useMemo(
    () => currentMonth.toLocaleDateString(undefined, { month: "long", year: "numeric" }),
    [currentMonth]
  );

  const fetchMonth = async (monthDate) => {
    const year = monthDate.getFullYear();
    const month = monthDate.getMonth();
    const key = `${year}-${pad(month + 1)}`;
    if (monthCache[key]) return;

    const start = new Date(year, month, 1);
    const end = new Date(year, month + 1, 0);
    const dateFrom = `${toDateKey(start)}T00:00:00`;
    const dateTo = `${toDateKey(end)}T23:59:59`;

    setMonthLoading(true);
    setMonthError("");
    try {
      // If total exceeds page_size, counts will reflect the first PAGE_SIZE_MONTH items.
      const data = await listAuditLogs({
        page: 1,
        page_size: PAGE_SIZE_MONTH,
        date_from: dateFrom,
        date_to: dateTo,
      });
      const items = data?.items || [];
      const countsByDay = {};
      items.forEach((entry) => {
        const d = getEntryDate(entry);
        if (!d) return;
        const keyDay = toDateKey(d);
        countsByDay[keyDay] = (countsByDay[keyDay] || 0) + 1;
      });
      setMonthCache((prev) => ({ ...prev, [key]: { items, countsByDay } }));
    } catch (err) {
      setMonthError(formatApiError(err));
    } finally {
      setMonthLoading(false);
    }
  };

  const fetchDay = async (dateKey) => {
    if (!dateKey) return;
    if (dayItems[dateKey]) return;
    setDayLoading(true);
    setDayError("");
    try {
      const data = await listAuditLogs({
        page: 1,
        page_size: PAGE_SIZE_DAY,
        date_from: `${dateKey}T00:00:00`,
        date_to: `${dateKey}T23:59:59`,
      });
      setDayItems((prev) => ({ ...prev, [dateKey]: data?.items || [] }));
    } catch (err) {
      const statusCode = err?.response?.status;
      if (statusCode === 404) {
        setDayItems((prev) => ({ ...prev, [dateKey]: [] }));
      } else {
        setDayError(formatApiError(err));
      }
    } finally {
      setDayLoading(false);
    }
  };

  useEffect(() => {
    fetchMonth(currentMonth);
  }, [currentMonth]);

  useEffect(() => {
    const today = new Date();
    const isSameMonth =
      today.getFullYear() === currentMonth.getFullYear() &&
      today.getMonth() === currentMonth.getMonth();
    if (isSameMonth && !selectedDate) {
      const todayKey = toDateKey(today);
      setSelectedDate(todayKey);
      fetchDay(todayKey);
    }
  }, [currentMonth, selectedDate]);

  const calendarCells = useMemo(() => {
    const year = currentMonth.getFullYear();
    const month = currentMonth.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const cells = [];
    for (let i = 0; i < firstDay; i += 1) {
      cells.push({ type: "empty", key: `empty-${i}` });
    }
    for (let day = 1; day <= daysInMonth; day += 1) {
      const date = new Date(year, month, day);
      cells.push({
        type: "day",
        key: toDateKey(date),
        day,
        dateKey: toDateKey(date),
      });
    }
    return cells;
  }, [currentMonth]);

  const countsByDay = monthCache[monthKey]?.countsByDay || {};
  const selectedItems = selectedDate ? dayItems[selectedDate] || [] : [];

  return (
    <div className="audit-calendar-page">
      <div className="diamond-pattern"></div>

      <main className="audit-calendar-main">
        <div className="audit-calendar-container">
          <div className="audit-calendar-header">
            <div>
              <h1 className="audit-page-title">Case Audit Log</h1>
              <div className="audit-calendar-subtitle">Calendar View</div>
            </div>
            <div className="audit-calendar-actions">
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => navigate("/admin/audit-log")}
              >
                Back to List View
              </button>
            </div>
          </div>

          {monthError && <div className="audit-error-banner">{monthError}</div>}

          <div className="audit-calendar-toolbar">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() =>
                setCurrentMonth(
                  new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1, 1)
                )
              }
            >
              Prev
            </button>
            <div className="audit-calendar-month">{monthLabel}</div>
            <button
              type="button"
              className="btn btn-secondary"
              onClick={() =>
                setCurrentMonth(
                  new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 1)
                )
              }
            >
              Next
            </button>
          </div>

          <div className="audit-calendar-layout">
            <div className="audit-calendar-card">
              <div className="audit-calendar-grid">
                {WEEKDAYS.map((label) => (
                  <div key={label} className="audit-calendar-weekday">
                    {label}
                  </div>
                ))}
                {calendarCells.map((cell) => {
                  if (cell.type === "empty") {
                    return <div key={cell.key} className="audit-calendar-cell empty" />;
                  }
                  const count = countsByDay[cell.dateKey] || 0;
                  const isSelected = selectedDate === cell.dateKey;
                  return (
                    <button
                      type="button"
                      key={cell.key}
                      className={`audit-calendar-cell day ${isSelected ? "selected" : ""}`}
                      onClick={() => {
                        setSelectedDate(cell.dateKey);
                        fetchDay(cell.dateKey);
                      }}
                    >
                      <span className="audit-calendar-day">{cell.day}</span>
                      {count > 0 && <span className="audit-calendar-count">{count}</span>}
                    </button>
                  );
                })}
              </div>
              {monthLoading && <div className="audit-calendar-loading">Loading month...</div>}
            </div>

            <div className="audit-calendar-details">
              <div className="audit-details-header">
                <div className="audit-details-title">
                  {selectedDate || "Select a date"}
                </div>
                {dayLoading && <span className="audit-details-status">Loading...</span>}
              </div>
              {dayError && <div className="audit-error-banner">{dayError}</div>}
              {!selectedDate && (
                <div className="audit-details-empty">Select a date to view audit entries.</div>
              )}
              {selectedDate && !dayLoading && selectedItems.length === 0 && (
                <div className="audit-details-empty">No audit actions for this date.</div>
              )}
              {selectedDate && selectedItems.length > 0 && (
                <ul className="audit-details-list">
                  {selectedItems.map((entry) => (
                    <li key={entry.id} className="audit-details-item">
                      <div className="audit-details-time">{formatTime(entry)}</div>
                      <div className="audit-details-body">
                        <div className="audit-details-action">{entry.action}</div>
                        <div className="audit-details-meta">
                          <span>{formatActor(entry)}</span>
                          <span className="audit-details-sep">•</span>
                          <span>{formatEntity(entry)}</span>
                        </div>
                        {entry.description && (
                          <div className="audit-details-desc">{entry.description}</div>
                        )}
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
