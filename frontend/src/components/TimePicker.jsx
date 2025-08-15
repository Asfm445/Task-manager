import React from "react";
import Flatpickr from "react-flatpickr";
import "flatpickr/dist/flatpickr.css";

export default function TimePicker({ value, onChange }) {
  const now = new Date(); // current time

  return (
    <Flatpickr
      value={value || now}
      options={{
        enableTime: true,
        noCalendar: true,
        dateFormat: "H:i", // 24-hour format, e.g. "14:30"
        time_24hr: true,
        defaultDate: now // set default time to now
      }}
      onChange={(selectedDates) => {
        if (selectedDates.length > 0) {
          onChange(selectedDates[0]);
        }
      }}
      className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
    />
  );
}
