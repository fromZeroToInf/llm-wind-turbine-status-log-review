
async function loadSignalChart(wt_id, timestamp, signal){
    const response = await fetch(`/api/reviews/${wt_id}/${timestamp}/${signal}`);
    const data = await response.json();
    console.log(data);
    console.log(data.window_start)
    console.log(data.window_end)
    const chartElem = document.getElementById("signal-chart");
    const chart = echarts.init(chartElem);

    chart.setOption({
    title: {
      text: `WT ${data.wt_id}`
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
        name:data.signal_name,
        type: "line",
        data: data.points,
        symbolSize: 1,
        markArea: {
          itemStyle: {
            color: 'rgba(94, 255, 0, 0.4)'
          },
          data: [
            [
              {
                name: '',
                xAxis: data.window_start
              },
              {
                xAxis: data.window_end
              }
            ]
          ]
        },

        markLine: {
          symbol: "none",
          label: {
            formatter: "Detection"
          },
          lineStyle: {
            type: "dashed"
          },
          data: [
            {
              name: "Detection",
              xAxis: data.detection_ts
            }
          ]
        },
        showSymbol: false
      }
    ]
  });
  
}

async function load_powercurve(wt_id, detection_ts, half_window_size){
  const response = await fetch(`/api/reviews/${wt_id}/${detection_ts}/${half_window_size}/powercurve`);
  const data = await response.json();
  const chartElem = document.getElementById("powercurve");
  const chart = echarts.init(chartElem);
  console.log(data.detection)
  chart.setOption({
         title: {
          text: `Power Curve`
        },
        xAxis: {
            type: "value",
            name: "Wind speed (m/s) at hub height"
        },
        yAxis: {
            type: "value",
            name: "Power (kW)"
        },
        series: [
          {
              name: "Power curve points",
              type: "line",
              symbolSize: 1,
              data: data.power_curve,
              lineStyle: {
                opacity: 0.1
              },
              itemStyle: {
                color: "grey"
              },
              z:1
          },
          {
            name: "Window data point",
            type: "scatter",
            data: data.window_data,
            symbolSize: 5,
            itemStyle: {
              color: "blue",
              opacity: 0.25
            },
            z:2
          },
          {
            name: "Detection point",
            type: "effectScatter",
            data: data.detection,
            symbolSize: 5,
            itemStyle: {
              color: "red"
            },
            z:3
          },
            
        ]
    });
}

async function load_review() {
    const parts = window.location.pathname.split("/");
    const detectionId = parts[2];
    
    const response = await fetch(`/api/reviews/${detectionId}`);
    const review = await response.json();
    
    document.getElementById("wt-id").textContent = review.wt_id;
    document.getElementById("detection-id").textContent = review.detection_id;
    document.getElementById("detection-idx").textContent = review.detection_index;
    document.getElementById("detection-ts").textContent = review.detection_ts;
    document.getElementById("relevant-signal").textContent = review.relevant_signal ;
    document.getElementById("anomaly-description-reasoning").textContent = review.anomaly_description_reasoning;

    var list = document.getElementById("relevant-logs");
    logs = review.relevant_logs;
    
    if (logs.length > 0) {
      var tr = document.createElement("tr");
      var cols = Object.keys(logs[0]);
      cols.forEach( (col) => {
          var th = document.createElement("th")
          var cell = document.createTextNode(col)
          th.appendChild(cell)
          tr.appendChild(th)
      })
      list.appendChild(tr)

   
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

    loadSignalChart(review.wt_id, review.detection_ts, review.relevant_signal);
    load_powercurve(review.wt_id, review.detection_ts, 24);
}

load_review();