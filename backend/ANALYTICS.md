# Task Analytics Documentation

## Overview

The Task Analytics system provides comprehensive insights into individual task performance, helping users understand their productivity patterns and make data-driven decisions.

## API Endpoint

```
GET /tasks/analytics/{task_id}
```

**Authentication Required:** Yes (JWT token)

**Response:** Comprehensive analytics data for the specified task

## Analytics Components

### 1. Completion Metrics

- **completion_rate**: Percentage of work completed (done_hours / estimated_hours)
- **remaining_hours**: Hours left to complete the task
- **done_hours**: Total hours worked on the task
- **estimated_hours**: Original time estimate
- **progress_percentage**: Visual progress indicator (capped at 100%)

### 2. Time Efficiency

- **efficiency_score**: Overall efficiency rating (0-100)
- **avg_hours_per_cycle**: Average hours per work cycle
- **cycles_completed**: Number of completed work cycles
- **total_cycles**: Total number of cycles
- **total_hours_worked**: Cumulative hours worked

### 3. Progress Trends

- **trend**: Performance trend ("improving", "declining", "stable", "no_data")
- **consistency_score**: How consistent your work patterns are (0-100)
- **improvement_rate**: Percentage improvement over time
- **cycles_analyzed**: Number of cycles used for trend analysis
- **recent_performance**: Last 3 cycles performance data

### 4. Performance Indicators

- **productivity_score**: Work output vs estimates (0-100)
- **reliability_score**: Consistency in meeting estimates (0-100)
- **quality_score**: Overall work quality based on completion rates (0-100)
- **overall_performance**: Weighted average of all performance metrics

### 5. Status Analysis

- **current_status**: Current task status
- **status_health**: Health indicator ("excellent", "good", "needs_attention", "warning")
- **status_duration_days**: Days in current status
- **status_changes**: Number of status changes
- **stop_frequency**: Number of times task was stopped (for repetitive tasks)
- **is_repetitive**: Whether task is repetitive
- **is_stopped**: Whether task is currently stopped

### 6. Time Analysis

- **time_spent_hours**: Total time spent on task
- **time_remaining_hours**: Time left until deadline
- **time_efficiency**: Hours of work per time spent
- **deadline_status**: Deadline status ("on_track", "approaching", "urgent", "overdue", "no_deadline")
- **start_date**: Task start date
- **end_date**: Task end date

### 7. Summary

- **grade**: Overall grade (A, B, C, D, F)
- **overall_score**: Combined performance score
- **recommendations**: Actionable improvement suggestions
- **key_insights**: Important highlights about the task

## Example Response

```json
{
  "task": {
    "id": 1,
    "description": "Complete project documentation",
    "start_date": "2024-01-01T00:00:00Z",
    "end_date": "2024-01-15T00:00:00Z",
    "estimated_hr": 40.0,
    "done_hr": 24.0,
    "status": "in_progress",
    "is_repititive": false
  },
  "analytics": {
    "completion_metrics": {
      "completion_rate": 60.0,
      "remaining_hours": 16.0,
      "done_hours": 24.0,
      "estimated_hours": 40.0,
      "progress_percentage": 60.0
    },
    "time_efficiency": {
      "efficiency_score": 85.0,
      "avg_hours_per_cycle": 4.0,
      "cycles_completed": 6,
      "total_cycles": 6,
      "total_hours_worked": 24.0
    },
    "progress_trends": {
      "trend": "improving",
      "consistency_score": 78.5,
      "improvement_rate": 15.2,
      "cycles_analyzed": 6,
      "recent_performance": [4.5, 5.0, 5.5]
    },
    "performance_indicators": {
      "productivity_score": 90.0,
      "reliability_score": 85.0,
      "quality_score": 88.0,
      "overall_performance": 87.7
    },
    "status_analysis": {
      "current_status": "in_progress",
      "status_health": "good",
      "status_duration_days": 7,
      "status_changes": 6,
      "stop_frequency": 0,
      "is_repetitive": false,
      "is_stopped": false
    },
    "time_analysis": {
      "time_spent_hours": 168.0,
      "time_remaining_hours": 168.0,
      "time_efficiency": 14.3,
      "deadline_status": "on_track",
      "start_date": "2024-01-01T00:00:00Z",
      "end_date": "2024-01-15T00:00:00Z"
    },
    "summary": {
      "grade": "B",
      "overall_score": 72.5,
      "recommendations": [
        "Keep up the good work!",
        "Consider increasing daily work hours to meet deadline"
      ],
      "key_insights": [
        "Task is 60.0% complete",
        "Efficiency score: 85.0%",
        "Status: in_progress"
      ]
    }
  }
}
```

## Use Cases

1. **Performance Monitoring**: Track how well you're meeting your time estimates
2. **Productivity Analysis**: Understand your work patterns and efficiency
3. **Deadline Management**: Get alerts about approaching deadlines
4. **Improvement Tracking**: See if your performance is improving over time
5. **Work Planning**: Use insights to better estimate future tasks

## Error Handling

- **404 Not Found**: Task doesn't exist
- **403 Forbidden**: User doesn't have access to the task
- **401 Unauthorized**: Invalid or missing authentication token

## Notes

- Analytics are calculated in real-time based on current task data
- For tasks with no progress history, many metrics will show 0 or "no_data"
- Repetitive tasks have additional analytics for cycle management
- All percentages are rounded to 2 decimal places
- Time calculations use UTC timezone
