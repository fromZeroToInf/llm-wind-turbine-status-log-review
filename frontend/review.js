
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

loadSignalChart();

async function load_review() {
    const parts = window.location.pathname.split("/");
    const detectionId = parts[2];
    
    const response = await fetch("/api/reviews/${detectionId}");
    const review = await response.json();

    document.getElementById("wt-id").textContent = review.wt_id;

    document.getElementById("detection-id").textContent = review.detection_id;

    document.getElementById("detection-ts").textContent = review.detection_ts;

    document.getElementById("relevant-signal").textContent = review.relevant_signal ;

    document.getElementById("anomaly-description-reasoning").textContent = review.anomaly_description_reasoning;

    var list = document.getElementById("relevant-logs");
    logs = review.relevant_logs;
    
    var tr = document.createElement("tr");
    var cols = Object.keys(logs[0])
    cols.forEach( (col) => {
        var th = document.createElement("th")
        var cell = document.createTextNode(col)
        th.appendChild(cell)
        tr.appendChild(th)
    })
    list.appendChild(tr)

    if (logs.length > 0) {
        logs.forEach( (dict) => {
            var tr = document.createElement("tr")
            var keys = Object.keys(dict)
            keys.forEach( (key) => {
                var td = document.createElement("td")
                var cell = document.createTextNode(dict[key])
                td.appendChild(cell)
                tr.appendChild(td)
            })
            list.appendChild(tr)
            
        })
    }
    
    document.getElementById("overall-assessment").textContent = review.overall_assessment;

    document.getElementById("overall-reasoning").textContent = review.overall_reasoning;

}

load_review();