document.addEventListener("DOMContentLoaded", () => {
  // Constants
  const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
  const HOURS = Array.from({ length: 14 }, (_, i) => i + 8) // 8 AM to 9 PM

  // State
  let scheduleData = {}
  let currentWeekStart = getStartOfWeek(new Date())
  let isDragging = false
  let dragStatus = null
  const workHourLimits = { min: 6, max: 10 }
  const breakSettings = {
    lunchBreak: true,
    lunchTime: "12",
    eveningBreak: false,
    eveningTime: "15",
  }
  const slotDuration = 30
  let selectedDay = null

  // Initialize schedule data
  function initializeScheduleData() {
    scheduleData = DAYS.reduce((acc, day) => {
      acc[day] = Array.from({ length: 14 }, (_, hour) => ({
        hour: hour + 8,
        status: hour >= 2 && hour <= 9 ? "available" : "unavailable", // 10 AM to 5 PM as available by default
        duration: 30,
      }))
      return acc
    }, {})

    // Add some breaks
    scheduleData["Monday"][4].status = "break" // 12 PM break
    scheduleData["Wednesday"][4].status = "break" // 12 PM break
    scheduleData["Friday"][4].status = "break" // 12 PM break

    // Add some booked slots
    scheduleData["Tuesday"][3].status = "booked" // 11 AM booked
    scheduleData["Thursday"][5].status = "booked" // 1 PM booked
    scheduleData["Thursday"][6].status = "booked" // 2 PM booked
  }

  // Initialize the UI
  function initializeUI() {
    renderTimeSlots()
    renderDayColumns()
    updateWeekRange()
    updateStats()
    setupEventListeners()
  }

  // Render time slots in the first column
  function renderTimeSlots() {
    const timeColumn = document.querySelector(".time-slots")
    timeColumn.innerHTML = ""

    HOURS.forEach((hour) => {
      const timeSlot = document.createElement("div")
      timeSlot.className = "h-14 flex items-center justify-center"
      timeSlot.innerHTML = `
        <div class="text-sm font-medium text-slate-600">
          ${hour}:00
          <span class="text-xs text-slate-400 ml-0.5">${hour < 12 ? "AM" : "PM"}</span>
        </div>
      `
      timeColumn.appendChild(timeSlot)
    })
  }

  // Render day columns
  function renderDayColumns() {
    const scheduleGrid = document.getElementById("schedule-grid")

    // Remove existing day columns
    const existingColumns = scheduleGrid.querySelectorAll(".day-column")
    existingColumns.forEach((col) => col.remove())

    // Add day columns
    DAYS.forEach((day, dayIndex) => {
      const isToday = dayIndex === new Date().getDay() - 1 // Adjust if your week starts with Sunday

      const dayColumn = document.createElement("div")
      dayColumn.className = "day-column text-center"
      dayColumn.dataset.day = day

      // Day header
      const dayHeader = document.createElement("div")
      dayHeader.className = `day-header ${isToday ? "today" : ""}`
      dayHeader.innerHTML = `
        <span class="text-sm font-bold ${isToday ? "text-indigo-700" : "text-slate-700"}">
          ${day.slice(0, 3)}
        </span>
        ${
          isToday
            ? `
          <span class="text-xs bg-indigo-600 text-white px-1.5 py-0.5 rounded-full mt-0.5">
            Today
          </span>
        `
            : ""
        }
        <div class="day-actions">
          <button class="day-menu-button inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors hover:bg-slate-200/70 rounded-full h-6 w-6 p-0" data-day="${day}">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-more-horizontal text-slate-500"><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/><circle cx="5" cy="12" r="1"/></svg>
          </button>
        </div>
      `
      dayColumn.appendChild(dayHeader)

      // Time slots
      scheduleData[day].forEach((slot, hourIndex) => {
        const timeSlot = document.createElement("div")
        timeSlot.className = `schedule-slot ${slot.status}`
        timeSlot.dataset.day = day
        timeSlot.dataset.hour = hourIndex

        let slotContent = ""
        if (slot.status === "booked") {
          slotContent = `
            <div class="flex flex-col items-center justify-center h-full">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-user text-red-500"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
              <span class="text-xs mt-1 text-red-600 font-medium">Booked</span>
            </div>
          `
        } else if (slot.status === "break") {
          slotContent = `
            <div class="flex flex-col items-center justify-center h-full">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-coffee text-amber-500"><path d="M17 8h1a4 4 0 1 1 0 8h-1"/><path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"/><line x1="6" x2="6" y1="2" y2="4"/><line x1="10" x2="10" y1="2" y2="4"/><line x1="14" x2="14" y1="2" y2="4"/></svg>
              <span class="text-xs mt-1 text-amber-600 font-medium">Break</span>
            </div>
          `
        } else if (slot.status === "available") {
          slotContent = `
            <div class="flex flex-col items-center justify-center h-full">
              <div class="w-2 h-2 rounded-full bg-emerald-500 mb-1"></div>
              <span class="text-xs text-emerald-600 font-medium">Available</span>
            </div>
          `
        } else {
          slotContent = `
            <div class="flex flex-col items-center justify-center h-full">
              <span class="text-xs text-slate-400">Free</span>
            </div>
          `
        }

        timeSlot.innerHTML = slotContent
        dayColumn.appendChild(timeSlot)
      })

      // Add warnings if needed
      const workingHours = calculateWorkingHours(day)
      if (workingHours > workHourLimits.max) {
        const warning = document.createElement("div")
        warning.className = "mt-2 text-xs font-medium px-2 py-1 bg-red-100 text-red-600 rounded-full inline-block"
        warning.textContent = "Exceeds max hours"
        dayColumn.appendChild(warning)
      } else if (workingHours > 0 && workingHours < workHourLimits.min) {
        const warning = document.createElement("div")
        warning.className = "mt-2 text-xs font-medium px-2 py-1 bg-amber-100 text-amber-600 rounded-full inline-block"
        warning.textContent = "Below min hours"
        dayColumn.appendChild(warning)
      }

      scheduleGrid.appendChild(dayColumn)
    })
  }

  // Update the week range display
  function updateWeekRange() {
    const weekRangeElement = document.getElementById("week-range")
    const endOfWeek = addDays(currentWeekStart, 6)
    weekRangeElement.textContent = `${formatDate(currentWeekStart, "MMM d")} - ${formatDate(endOfWeek, "MMM d, yyyy")}`
  }

  // Calculate working hours for a day
  function calculateWorkingHours(day) {
    return scheduleData[day].filter((slot) => slot.status === "available").length / 2 // Convert 30-min slots to hours
  }

  // Calculate total weekly hours
  function calculateTotalWeeklyHours() {
    return DAYS.reduce((total, day) => total + calculateWorkingHours(day), 0)
  }

  // Update statistics
  function updateStats() {
    const totalWeeklyHours = calculateTotalWeeklyHours()

    // Update header stats
    document.getElementById("total-weekly-hours").textContent = `${totalWeeklyHours}h`
    document.getElementById("footer-weekly-hours").textContent = `${totalWeeklyHours}h`

    // Update stats tab
    document.getElementById("stats-total-hours").textContent = `${totalWeeklyHours} hours`

    const workingDays = DAYS.filter((day) => calculateWorkingHours(day) > 0).length
    document.getElementById("stats-working-days").textContent = `${workingDays} days`

    const avgHoursPerDay = workingDays > 0 ? (totalWeeklyHours / workingDays).toFixed(1) : "0.0"
    document.getElementById("stats-avg-hours").textContent = `${avgHoursPerDay} hours`

    const totalBreaks = DAYS.reduce((total, day) => {
      return total + scheduleData[day].filter((slot) => slot.status === "break").length
    }, 0)
    document.getElementById("stats-breaks").textContent = `${totalBreaks} slots`

    // Update workload distribution
    const workloadStats = document.getElementById("workload-stats")
    workloadStats.innerHTML = ""

    DAYS.forEach((day) => {
      const hours = calculateWorkingHours(day)
      const barColor =
        hours > workHourLimits.max
          ? "bg-red-400"
          : hours < workHourLimits.min && hours > 0
            ? "bg-amber-400"
            : "bg-emerald-400"

      const dayStats = document.createElement("div")
      dayStats.className = "space-y-1"
      dayStats.innerHTML = `
        <div class="flex justify-between items-center">
          <span class="text-sm">${day}</span>
          <span class="text-sm font-medium">${hours} hrs</span>
        </div>
        <div class="w-full bg-gray-100 rounded-full h-2">
          <div class="h-2 rounded-full ${barColor}" style="width: ${(hours / 12) * 100}%"></div>
        </div>
      `

      workloadStats.appendChild(dayStats)
    })

    // Update recommendations
    updateRecommendations()

    // Update warnings
    updateWarnings()
  }

  // Update recommendations
  function updateRecommendations() {
    const recommendations = document.getElementById("recommendations")
    recommendations.innerHTML = ""

    // Check for days exceeding max hours
    const daysExceedingMaxHours = DAYS.filter((day) => calculateWorkingHours(day) > workHourLimits.max)
    if (daysExceedingMaxHours.length > 0) {
      const rec = document.createElement("div")
      rec.className = "text-sm space-y-1"
      rec.innerHTML = `
        <div class="font-medium text-red-600">High Workload Days</div>
        <p>Consider reducing hours on: ${daysExceedingMaxHours.join(", ")}</p>
      `
      recommendations.appendChild(rec)
    }

    // Check for days below min hours
    const daysBelowMinHours = DAYS.filter((day) => {
      const hours = calculateWorkingHours(day)
      return hours < workHourLimits.min && hours > 0
    })

    if (daysBelowMinHours.length > 0) {
      const rec = document.createElement("div")
      rec.className = "text-sm space-y-1"
      rec.innerHTML = `
        <div class="font-medium text-amber-600">Low Workload Days</div>
        <p>Consider increasing hours on: ${daysBelowMinHours.join(", ")}</p>
      `
      recommendations.appendChild(rec)
    }

    // Check for days without breaks
    const daysWithoutBreaks = DAYS.filter((day) => !scheduleData[day].some((slot) => slot.status === "break"))

    if (daysWithoutBreaks.length > 0) {
      const rec = document.createElement("div")
      rec.className = "text-sm space-y-1"
      rec.innerHTML = `
        <div class="font-medium text-blue-600">Missing Breaks</div>
        <p>Some days have no scheduled breaks. Consider adding breaks for better productivity.</p>
      `
      recommendations.appendChild(rec)
    }

    // Check for work-life balance
    const daysOff = DAYS.filter((day) => calculateWorkingHours(day) === 0)
    if (daysOff.length > 2) {
      const rec = document.createElement("div")
      rec.className = "text-sm space-y-1"
      rec.innerHTML = `
        <div class="font-medium text-emerald-600">Work-Life Balance</div>
        <p>You have multiple days off. Great job maintaining work-life balance!</p>
      `
      recommendations.appendChild(rec)
    }
  }

  // Update warnings
  function updateWarnings() {
    const warningsCard = document.getElementById("schedule-warnings")
    const warningContent = document.getElementById("warning-content")
    warningContent.innerHTML = ""

    // Check for days exceeding max hours
    const daysExceedingMaxHours = DAYS.filter((day) => calculateWorkingHours(day) > workHourLimits.max)

    // Check for days below min hours
    const daysBelowMinHours = DAYS.filter((day) => {
      const hours = calculateWorkingHours(day)
      return hours < workHourLimits.min && hours > 0
    })

    if (daysExceedingMaxHours.length > 0 || daysBelowMinHours.length > 0) {
      warningsCard.classList.remove("hidden")

      if (daysExceedingMaxHours.length > 0) {
        const warning = document.createElement("div")
        warning.className = "flex items-start gap-2 mb-2"
        warning.innerHTML = `
          <div class="mt-1 min-w-4">
            <div class="w-2 h-2 rounded-full bg-red-500"></div>
          </div>
          <p class="text-amber-800">
            <span class="font-medium">Maximum Hours Exceeded:</span> ${daysExceedingMaxHours.join(", ")}
          </p>
        `
        warningContent.appendChild(warning)
      }

      if (daysBelowMinHours.length > 0) {
        const warning = document.createElement("div")
        warning.className = "flex items-start gap-2"
        warning.innerHTML = `
          <div class="mt-1 min-w-4">
            <div class="w-2 h-2 rounded-full bg-amber-500"></div>
          </div>
          <p class="text-amber-800">
            <span class="font-medium">Minimum Hours Not Met:</span> ${daysBelowMinHours.join(", ")}
          </p>
        `
        warningContent.appendChild(warning)
      }
    } else {
      warningsCard.classList.add("hidden")
    }
  }

  // Set up event listeners
  function setupEventListeners() {
    // Tab switching
    const tabTriggers = document.querySelectorAll(".tab-trigger")
    tabTriggers.forEach((trigger) => {
      trigger.addEventListener("click", () => {
        const tabId = trigger.dataset.tab

        // Update active tab trigger
        tabTriggers.forEach((t) => t.classList.remove("active"))
        trigger.classList.add("active")

        // Update active tab content
        const tabContents = document.querySelectorAll(".tab-content")
        tabContents.forEach((content) => content.classList.remove("active"))
        document.getElementById(`${tabId}-tab`).classList.add("active")
      })
    })

    // Week navigation
    document.getElementById("prev-week").addEventListener("click", () => {
      currentWeekStart = addDays(currentWeekStart, -7)
      updateWeekRange()
    })

    document.getElementById("next-week").addEventListener("click", () => {
      currentWeekStart = addDays(currentWeekStart, 7)
      updateWeekRange()
    })

    // Schedule slot interactions
    document.addEventListener("click", (event) => {
      const slot = event.target.closest(".schedule-slot")
      if (slot) {
        const day = slot.dataset.day
        const hourIndex = Number.parseInt(slot.dataset.hour)
        handleSlotClick(day, hourIndex)
      }
    })

    document.addEventListener("mousedown", (event) => {
      const slot = event.target.closest(".schedule-slot")
      if (slot) {
        const day = slot.dataset.day
        const hourIndex = Number.parseInt(slot.dataset.hour)
        handleDragStart(day, hourIndex)
      }
    })

    document.addEventListener("mouseover", (event) => {
      const slot = event.target.closest(".schedule-slot")
      if (slot && isDragging) {
        const day = slot.dataset.day
        const hourIndex = Number.parseInt(slot.dataset.hour)
        handleDragOver(day, hourIndex)
      }

      // Show tooltip
      if (slot) {
        showTooltip(slot, event)
      }
    })

    document.addEventListener("mouseout", (event) => {
      const slot = event.target.closest(".schedule-slot")
      if (slot) {
        hideTooltip()
      }
    })

    document.addEventListener("mouseup", () => {
      handleDragEnd()
    })

    // Day menu buttons
    document.addEventListener("click", (event) => {
      const menuButton = event.target.closest(".day-menu-button")
      if (menuButton) {
        const day = menuButton.dataset.day
        showDayMenu(day, menuButton)
        event.stopPropagation()
      }
    })

    // Clear day action
    document.getElementById("clear-day").addEventListener("click", () => {
      if (selectedDay) {
        clearDay(selectedDay)
        hideDayMenu()
      }
    })

    // Preset buttons
    const presetButtons = document.querySelectorAll(".preset-button")
    presetButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const preset = button.dataset.preset
        applyPreset(preset)
      })
    })

    // Break settings
    document.getElementById("lunch-break").addEventListener("change", (event) => {
      breakSettings.lunchBreak = event.target.checked
      document.getElementById("lunch-time-container").style.display = event.target.checked ? "block" : "none"
    })

    document.getElementById("evening-break").addEventListener("change", (event) => {
      breakSettings.eveningBreak = event.target.checked
      document.getElementById("evening-time-container").style.display = event.target.checked ? "block" : "none"
    })

    document.getElementById("lunch-time").addEventListener("change", (event) => {
      breakSettings.lunchTime = event.target.value
    })

    document.getElementById("evening-time").addEventListener("change", (event) => {
      breakSettings.eveningTime = event.target.value
    })

    document.getElementById("apply-breaks").addEventListener("click", applyBreakSettings)

    // Working hour limits
    document.getElementById("min-hours").addEventListener("change", (event) => {
      workHourLimits.min = Number.parseInt(event.target.value)
      updateStats()
    })

    document.getElementById("max-hours").addEventListener("change", (event) => {
      workHourLimits.max = Number.parseInt(event.target.value)
      updateStats()
    })

    // Custom template dialog
    document.getElementById("custom-template-btn").addEventListener("click", showCustomTemplateDialog)
    document.getElementById("cancel-template").addEventListener("click", hideCustomTemplateDialog)
    document.getElementById("save-template").addEventListener("click", saveCustomTemplate)

    // Day selection in custom template
    const daySelectButtons = document.querySelectorAll(".day-select")
    daySelectButtons.forEach((button) => {
      button.addEventListener("click", () => {
        button.classList.toggle("day-selected")
      })
    })

    // Close menus when clicking outside
    document.addEventListener("click", (event) => {
      if (!event.target.closest(".dropdown-menu") && !event.target.closest(".day-menu-button")) {
        hideDayMenu()
      }

      if (!event.target.closest(".dialog-content") && !event.target.closest("#custom-template-btn")) {
        hideCustomTemplateDialog()
      }
    })

    // Save button
    document.getElementById("save-button").addEventListener("click", saveSchedule)
  }

  // Handle slot click
  function handleSlotClick(day, hourIndex) {
    const currentStatus = scheduleData[day][hourIndex].status

    // Can't modify booked slots
    if (currentStatus === "booked") return

    const newStatus = currentStatus === "available" ? "break" : currentStatus === "break" ? "unavailable" : "available"

    scheduleData[day][hourIndex].status = newStatus
    renderDayColumns()
    updateStats()
  }

  // Handle drag start
  function handleDragStart(day, hourIndex) {
    const status = scheduleData[day][hourIndex].status
    if (status === "booked") return // Can't modify booked slots

    isDragging = true
    dragStatus = status === "available" ? "unavailable" : "available"
  }

  // Handle drag over
  function handleDragOver(day, hourIndex) {
    if (!isDragging || scheduleData[day][hourIndex].status === "booked") return

    scheduleData[day][hourIndex].status = dragStatus
    renderDayColumns()
    updateStats()
  }

  // Handle drag end
  function handleDragEnd() {
    isDragging = false
    dragStatus = null
  }

  // Show day menu
  function showDayMenu(day, button) {
    selectedDay = day
    const menu = document.getElementById("day-actions-menu")
    menu.classList.remove("hidden")

    // Position the menu
    const rect = button.getBoundingClientRect()
    menu.style.top = `${rect.bottom + window.scrollY}px`
    menu.style.left = `${rect.left + window.scrollX}px`

    // Generate copy options
    const copyOptions = document.getElementById("copy-day-options")
    copyOptions.innerHTML = ""

    DAYS.filter((d) => d !== day).forEach((otherDay) => {
      const option = document.createElement("button")
      option.className = "dropdown-item"
      option.innerHTML = `
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-copy mr-2"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>
        ${otherDay}
      `
      option.addEventListener("click", () => {
        copyDay(day, otherDay)
        hideDayMenu()
      })
      copyOptions.appendChild(option)
    })
  }

  // Hide day menu
  function hideDayMenu() {
    document.getElementById("day-actions-menu").classList.add("hidden")
    selectedDay = null
  }

  // Show tooltip
  function showTooltip(slot, event) {
    const tooltip = document.getElementById("tooltip")
    const tooltipContent = document.getElementById("tooltip-content")

    const day = slot.dataset.day
    const hourIndex = Number.parseInt(slot.dataset.hour)
    const status = scheduleData[day][hourIndex].status

    tooltipContent.innerHTML = `
      <div class="text-xs">
        <div class="font-medium">${day}, ${hourIndex + 8}:00 ${hourIndex + 8 < 12 ? "AM" : "PM"}</div>
        <div class="capitalize">${status}</div>
        ${status !== "booked" ? '<div class="mt-1 text-slate-300">Click to change status</div>' : ""}
      </div>
    `

    tooltip.classList.remove("hidden")

    // Position the tooltip
    const rect = slot.getBoundingClientRect()
    tooltip.style.top = `${rect.top + window.scrollY - 5}px`
    tooltip.style.left = `${rect.right + window.scrollX + 10}px`
  }

  // Hide tooltip
  function hideTooltip() {
    document.getElementById("tooltip").classList.add("hidden")
  }

  // Clear day
  function clearDay(day) {
    scheduleData[day] = scheduleData[day].map((slot) => ({
      ...slot,
      status: slot.status === "booked" ? "booked" : "unavailable",
    }))

    renderDayColumns()
    updateStats()
  }

  // Copy day
  function copyDay(fromDay, toDay) {
    scheduleData[toDay] = [...scheduleData[fromDay]]
    renderDayColumns()
    updateStats()
  }

  // Apply preset
  function applyPreset(preset) {
    DAYS.forEach((day) => {
      scheduleData[day] = scheduleData[day].map((slot, index) => {
        if (slot.status === "booked") return slot // Don't modify booked slots

        let newStatus = "unavailable"

        if (preset === "full-day" && index >= 1 && index <= 10) {
          // 9 AM to 6 PM
          newStatus = "available"
        } else if (preset === "morning" && index >= 0 && index <= 4) {
          // 8 AM to 12 PM
          newStatus = "available"
        } else if (preset === "evening" && index >= 7 && index <= 13) {
          // 3 PM to 9 PM
          newStatus = "available"
        }

        return {
          ...slot,
          status: newStatus,
        }
      })
    })

    renderDayColumns()
    updateStats()
  }

  // Apply break settings
  function applyBreakSettings() {
    DAYS.forEach((day) => {
      // Apply lunch break
      if (breakSettings.lunchBreak) {
        const lunchHour = Number.parseInt(breakSettings.lunchTime) - 8 // Convert to array index
        if (lunchHour >= 0 && lunchHour < scheduleData[day].length) {
          scheduleData[day][lunchHour].status = "break"
        }
      }

      // Apply evening break
      if (breakSettings.eveningBreak) {
        const eveningHour = Number.parseInt(breakSettings.eveningTime) - 8 // Convert to array index
        if (eveningHour >= 0 && eveningHour < scheduleData[day].length) {
          scheduleData[day][eveningHour].status = "break"
        }
      }
    })

    renderDayColumns()
    updateStats()
  }

  // Show custom template dialog
  function showCustomTemplateDialog() {
    document.getElementById("custom-template-dialog").classList.remove("hidden")
  }

  // Hide custom template dialog
  function hideCustomTemplateDialog() {
    document.getElementById("custom-template-dialog").classList.add("hidden")
  }

  // Save custom template
  function saveCustomTemplate() {
    const templateName = document.getElementById("template-name").value
    const startTime = Number.parseInt(document.getElementById("start-time").value)
    const endTime = Number.parseInt(document.getElementById("end-time").value)

    const selectedDays = []
    document.querySelectorAll(".day-select.day-selected").forEach((button) => {
      selectedDays.push(button.dataset.day)
    })

    if (templateName && selectedDays.length > 0) {
      selectedDays.forEach((day) => {
        scheduleData[day] = scheduleData[day].map((slot, index) => {
          if (slot.status === "booked") return slot // Don't modify booked slots

          const hour = index + 8
          const newStatus = hour >= startTime && hour < endTime ? "available" : "unavailable"

          return {
            ...slot,
            status: newStatus,
          }
        })
      })

      renderDayColumns()
      updateStats()
      hideCustomTemplateDialog()

      // Reset form
      document.getElementById("template-name").value = ""
      document.querySelectorAll(".day-select").forEach((button) => {
        button.classList.remove("day-selected")
      })
    } else {
      alert("Please enter a template name and select at least one day.")
    }
  }

  // Save schedule
  function saveSchedule() {
    alert("Schedule saved successfully!")
    // In a real application, this would send the data to a server
  }

  // Helper functions
  function getStartOfWeek(date) {
    const day = date.getDay()
    const diff = date.getDate() - day + (day === 0 ? -6 : 1) // Adjust when day is Sunday
    return new Date(date.setDate(diff))
  }

  function addDays(date, days) {
    const result = new Date(date)
    result.setDate(result.getDate() + days)
    return result
  }

  function formatDate(date, format) {
    // Simple date formatter
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    const d = date.getDate()
    const m = months[date.getMonth()]
    const y = date.getFullYear()

    return format.replace("MMM", m).replace("d", d).replace("yyyy", y)
  }

  // Initialize the application
  initializeScheduleData()
  initializeUI()
})

