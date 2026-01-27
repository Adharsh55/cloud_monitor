// 1. Setup Charts
const createChart = (ctx, color, label) => new Chart(ctx, {
    type: 'line',
    data: {
        labels: Array(20).fill(""),
        datasets: [{
            label: label,
            data: Array(20).fill(0),
            borderColor: color,
            backgroundColor: color + "20", // Transparent fill
            fill: true,
            tension: 0.4,
            pointRadius: 0
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { 
            y: { beginAtZero: true, max: 100, grid: { color: "#333" } },
            x: { display: false }
        }
    }
});

const cpuChart = createChart(document.getElementById("cpuChart").getContext("2d"), "#00e5ff", "CPU %");
const memChart = createChart(document.getElementById("memChart").getContext("2d"), "#f1c40f", "RAM %");

// 2. Update Function
async function update() {
    try {
        const res = await fetch("/api/data");
        const data = await res.json();
        
        // Update Charts
        [cpuChart, memChart].forEach(c => {
            c.data.datasets[0].data.shift();
            // Push new value (CPU or RAM)
            const val = c === cpuChart ? data.metrics.cpu : data.metrics.memory.percent;
            c.data.datasets[0].data.push(val);
            c.update();
        });

        // Update Logs Table
        const tbody = document.querySelector("#logTable tbody");
        tbody.innerHTML = "";
        
        data.logs.slice().reverse().slice(0, 8).forEach(line => {
            const parts = line.split(" | ");
            if(parts.length < 3) return;
            
            const [time, level, msg] = parts;
            let badge = "info";
            if(level === "WARNING") badge = "warning";
            if(level === "SUCCESS") badge = "success";

            tbody.innerHTML += `
                <tr>
                    <td style="color:#666; font-family:monospace">${time}</td>
                    <td><span class="badge ${badge}">${level}</span></td>
                    <td style="color:#eee">${msg}</td>
                </tr>
            `;
        });

    } catch (e) { console.error(e); }
}

setInterval(update, 2000);
update();