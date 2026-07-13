console.log("app.js loaded")

async function loadTestSignal() {
    const response = await fetch("/api/test-signal");
    const data = await response.json();

    console.log(data);
}


async function loadSignalChart(){
    const response = await fetch("/api/test-signal");
    const data = await response.json();

    const chartElem = document.getElementById("signal-chart");
    const chart = echarts.init(chartElem)

    chart.setOption({
    title: {
      text: "Test signal"
    },
    tooltip: {
      trigger: "axis"
    },
    xAxis: {
      type: "time"
    },
    yAxis: {
      type: "value"
    },
    series: [
      {
        name: "Signal",
        type: "line",
        data: data.points,
        showSymbol: false
      }
    ]
  });
}

//loadSignalChart();

async function loadDetections() {
    const response = await fetch("/api/detections");
    const detections = await response.json();
    const list = document.getElementById("detection-list");

    const columns = Object.keys(detections[0]);
    // Header of table
    var tr = document.createElement("tr");
    columns.forEach( (col) => {
        var th = document.createElement("th") 
        var cell = document.createTextNode(col);
        th.appendChild(cell)
        tr.appendChild(th);
    })

    var th = document.createElement("th");
    var cell = document.createTextNode("");
    th.appendChild(cell);
    tr.appendChild(th);
    list.appendChild(tr)

    detections.forEach( (detection) => {
        var keys = Object.keys(detection)
        var tr = document.createElement("tr");
        keys.forEach( (key) => {
            var td = document.createElement("td")
            var cell = document.createTextNode(detection[key]);
            td.appendChild(cell);
            tr.appendChild(td) 
        })
        var td = document.createElement("td")
        var button = document.createElement("button")
        button.addEventListener("click", () => {
            window.location.href = `/review/${detection.detection_id}`;
        })
        var btn_text = document.createTextNode("Inspect");
        button.appendChild(btn_text);
        td.appendChild(button)
        tr.appendChild(td);
        list.appendChild(tr);
    });
}

loadDetections();