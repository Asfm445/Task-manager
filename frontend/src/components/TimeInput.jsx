import React, { useState } from "react";

function TimeInput() {
  const getCurrentTime = () => {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    return `${hours}:${minutes}`;
  };

  const [form, setForm] = useState({
    start_time: getCurrentTime(),
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  return (
    <input
      id="start_time"
      type="time"
      name="start_time"
      value={form.start_time}
      onChange={handleChange}
      className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-400"
    />
  );
}

export default TimeInput;
