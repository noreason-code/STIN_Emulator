import * as echarts from 'echarts'
import React from "react";

export default class ChatsDrawer extends React.Component {

    constructor(props) {
        super()
        this.get_chart_work = props.get_chart_work
        this.get_clear_chart = props.get_clear_chart
        this.set_chart_callback = props.set_chart_callback
    }

    componentDidMount() {
        console.log("componentDidMount")
        const chartRealTimeRTT = echarts.init(document.getElementById("RealTimeRTT"));
        // const chartRealTimeThroughputSnd = echarts.init(document.getElementById("RealTimeThroughputSnd"));
        const chartRealTimeThroughputRcv = echarts.init(document.getElementById("RealTimeThroughputRcv"));
        const chartTimeAverageFCT = echarts.init(document.getElementById("TimeAverageFCT"));
        const chartTimeAverageSlowdown = echarts.init(document.getElementById("TimeAverageSlowdown"));
        let RealTimeRTT_Conn1 = [];
        let RealTimeRTT_Conn2 = [];
        let RealTimeRTT_Conn3 = [];
        let RealTimeThroughput_Sender1 = [];
        let RealTimeThroughput_Sender2 = [];
        let RealTimeThroughput_Sender3 = [];
        let RealTimeThroughput_Receiver1 = [];
        let RealTimeThroughput_Receiver2 = [];
        let RealTimeThroughput_Receiver3 = [];
        let RealTimeRTT_TimeAxis = [];
        let RealTime_TimeAxis = [];
        let RealTime_CurTime = 0;
        let TimeAverageFCT_Conn1 = [];
        let TimeAverageFCT_Conn2 = [];
        let TimeAverageFCT_Conn3 = [];
        let TimeAverageFCT_TimeAxis = [];
        let TimeAverageFCT_CurTime = 0;
        let TimeAverageSlowdown_Conn1 = [];
        let TimeAverageSlowdown_Conn2 = [];
        let TimeAverageSlowdown_Conn3 = [];
        let axisTime = [];

        const updateThroughput = (data) => {
            if (this.get_chart_work()) {
                RealTime_CurTime += 1
                RealTime_TimeAxis.push(RealTime_CurTime)
                RealTimeThroughput_Receiver1.push(data)
            }
            // chartRealTimeThroughputSnd.setOption(
            //     {
            //         // title: {
            //         //     text: "Sender"
            //         // },
            //         legend: {
            //             data: ["Sender-1", "Sender-2", "Sender-3"],
            //             textStyle: {
            //                 color: 'rgb(166, 173, 180)'
            //             },
            //             orient: 'vertical',
            //             left: 'right'
            //         },
            //         xAxis: {
            //             data: RealTime_TimeAxis.slice(2),
            //             // name: "Time (s)",
            //             axisLabel: {formatter: "{value} s"}
            //         },
            //         yAxis: {
            //             splitLine:{
            //                 show:true,
            //                 lineStyle:{
            //                     type: 'dashed',
            //                     color: 'rgb(166, 173, 180)'
            //                 }
            //             },
            //             axisLabel: {
            //                 margin: 2,
            //                 formatter: function (value, index) {
            //                     if (value >= 1000 && value < 10000000) {
            //                         value = value / 1000 + "K";
            //                     } else if (value >= 1000000) {
            //                         value = value / 1000000 + "M";
            //                     }
            //                     return value;
            //                 }
            //             },
            //             // name: "Throughput (KB/s)",
            //             // nameRotate: 90,
            //             // nameLocation: 'mid',
            //             // nameTextStyle: {
            //             //     fontSize: 11
            //             // }
            //         },
            //         series: [
            //             {
            //                 symbol: "none",
            //                 name: "Sender-1",
            //                 type: "line",
            //                 data: RealTimeThroughput_Sender1.slice(2)
            //             },
            //             {
            //                 symbol: "none",
            //                 name: "Sender-2",
            //                 type: "line",
            //                 data: RealTimeThroughput_Sender2.slice(2)
            //             },
            //             {
            //                 symbol: "none",
            //                 name: "Sender-3",
            //                 type: "line",
            //                 data: RealTimeThroughput_Sender3.slice(2)
            //             }
            //         ]
            //     }
            // )
            chartRealTimeThroughputRcv.setOption(
                {
                    // title: {
                    //     text: "Receiver"
                    // },
                    legend: {
                        data: ["Receiver-1", "Receiver-2", "Receiver-3"],
                        textStyle: {
                            color: 'rgb(166, 173, 180)'
                        },
                        orient: 'vertical',
                        left: 'right'
                    },
                    xAxis: {
                        data: RealTime_TimeAxis.slice(2),
                        // name: "Time (s)",
                        axisLabel: {formatter: "{value} s"}
                    },
                    yAxis: {
                        splitLine:{
                            show:true,
                            lineStyle:{
                                type: 'dashed',
                                color: 'rgb(166, 173, 180)'
                            }
                        }
                        // name: "Throughput (KB/s)",
                        // nameRotate: 90,
                        // nameLocation: 'mid',
                        // nameTextStyle: {
                        //     fontSize: 11
                        // }
                    },
                    series: [
                        {
                            symbol: "none",
                            name: "Receiver-1",
                            type: "line",
                            data: RealTimeThroughput_Receiver1.slice(2)
                        },
                        {
                            symbol: "none",
                            name: "Receiver-2",
                            type: "line",
                            data: RealTimeThroughput_Receiver2.slice(2)
                        },
                        {
                            symbol: "none",
                            name: "Receiver-3",
                            type: "line",
                            data: RealTimeThroughput_Receiver3.slice(2)
                        }
                    ]
                }
            )
        }

        const updateRTT = (data) => {
            if (this.get_chart_work()) {
                RealTimeRTT_TimeAxis.push(RealTime_CurTime)
                RealTimeRTT_Conn1.push(data)
            }
            chartRealTimeRTT.setOption(
                {
                    // title: {
                    //     text: "Real-Time RTT"
                    // },
                    legend: {
                        data: ["Conn-1", "Conn-2", "Conn-3"],
                        textStyle: {
                            color: 'rgb(166, 173, 180)'
                        }
                    },
                    xAxis: {
                        data: RealTimeRTT_TimeAxis.slice(2),
                        // name: "Time (s)",
                        axisLabel: {formatter: "{value} s"}
                    },
                    yAxis: {
                        splitLine:{
                            show:true,
                            lineStyle:{
                                type: 'dashed',
                                color: 'rgb(166, 173, 180)'
                            }
                        }
                        // name: "RTT (ms)",
                        // nameRotate: 90,
                        // nameLocation: 'mid'
                    },
                    series: [
                        {
                            symbol: "none",
                            name: "Conn-1",
                            type: "line",
                            data: RealTimeRTT_Conn1.slice(2)
                        },
                        {
                            symbol: "none",
                            name: "Conn-2",
                            type: "line",
                            data: RealTimeRTT_Conn2.slice(2)
                        },
                        {
                            symbol: "none",
                            name: "Conn-3",
                            type: "line",
                            data: RealTimeRTT_Conn3.slice(2)
                        }
                    ]
                }
            )
        }

        const updateFCT = (data) => {
            if (this.get_chart_work()) {
                TimeAverageFCT_CurTime += 2
                TimeAverageFCT_TimeAxis.push(TimeAverageFCT_CurTime)
                const len = TimeAverageFCT_Conn1.length
                const new_data = 1.0 * ((len > 0) ? (TimeAverageFCT_Conn1[len - 1] * len + data) : data) / (len + 1);
                TimeAverageFCT_Conn1.push(new_data)
            }
            chartTimeAverageFCT.setOption(
                {
                    // title: {
                    //     text: "Time Average FCT"
                    // },
                    legend: {
                        data: ["Conn-1", "Conn-2", "Conn-3"],
                        textStyle: {
                            color: 'rgb(166, 173, 180)'
                        }
                    },
                    xAxis: {
                        data: TimeAverageFCT_TimeAxis.slice(2),
                        // name: "Time (s)",
                        axisLabel: {formatter: "{value} s"}
                    },
                    yAxis: {
                        splitLine:{
                            show:true,
                            lineStyle:{
                                type: 'dashed',
                                color: 'rgb(166, 173, 180)'
                            }
                        }
                        // name: "Time Average FCT",
                        // nameRotate: 90,
                        // nameLocation: 'mid',
                        // nameTextStyle: {
                        //     padding: [0, 0, 0, 0]
                        // }
                    },
                    series: [
                        {
                            symbol: "none",
                            name: "Conn-1",
                            type: "line",
                            data: TimeAverageFCT_Conn1.slice(2)
                        },
                        {
                            symbol: "none",
                            name: "Conn-2",
                            type: "line",
                            data: TimeAverageFCT_Conn2.slice(2)
                        },
                        {
                            symbol: "none",
                            name: "Conn-3",
                            type: "line",
                            data: TimeAverageFCT_Conn3.slice(2)
                        }
                    ]
                }
            )
        }

        const update = (data) => {

            chartTimeAverageSlowdown.setOption(
                {
                    // title: {
                    //     text: "Time Average Slowdown"
                    // },
                    legend: {
                        data: ["Conn-1", "Conn-2", "Conn-3"],
                        textStyle: {
                            color: 'rgb(166, 173, 180)'
                        }
                    },
                    xAxis: {
                        data: axisTime.slice(2),
                        // name: "Time (s)",
                        axisLabel: {formatter: "{value} s"}
                    },
                    yAxis: {
                        splitLine:{
                            show:true,
                            lineStyle:{
                                type: 'dashed',
                                color: 'rgb(166, 173, 180)'
                            }
                        }
                        // name: "Time Average Slowdown",
                        // nameRotate: 90,
                        // nameLocation: 'mid'
                    },
                    series: [
                        {
                            symbol: "none",
                            name: "Conn-1",
                            type: "line",
                            data: TimeAverageSlowdown_Conn1.slice(2)
                        },
                        {
                            symbol: "none",
                            name: "Conn-2",
                            type: "line",
                            data: TimeAverageSlowdown_Conn2.slice(2)
                        },
                        {
                            symbol: "none",
                            name: "Conn-3",
                            type: "line",
                            data: TimeAverageSlowdown_Conn3.slice(2)
                        }
                    ]
                }
            )
        }

        const clearChart = () => {
            RealTimeRTT_Conn1 = []
            RealTimeRTT_Conn2 = []
            RealTimeRTT_Conn3 = []
            RealTimeRTT_TimeAxis = []
            RealTimeThroughput_Sender1 = []
            RealTimeThroughput_Sender2 = []
            RealTimeThroughput_Sender3 = []
            RealTimeThroughput_Receiver1 = []
            RealTimeThroughput_Receiver2 = []
            RealTimeThroughput_Receiver3 = []
            RealTime_TimeAxis = []
            TimeAverageFCT_Conn1 = []
            TimeAverageFCT_Conn2 = []
            TimeAverageFCT_Conn3 = []
            TimeAverageFCT_TimeAxis = []
            TimeAverageSlowdown_Conn1 = []
            TimeAverageSlowdown_Conn2 = []
            TimeAverageSlowdown_Conn3 = []
            axisTime = []
            TimeAverageFCT_CurTime = 0
            RealTime_CurTime = 0
        }

        this.updateFn = {
            "clear": clearChart,
            "throughput": updateThroughput,
            "rtt": updateRTT,
            "fct": updateFCT
        }
        this.set_chart_callback(this.updateFn)
        for (let k in this.updateFn) {
            this.updateFn[k](0)
        }

        // 定时检测清空
        setInterval(() => {
            if (this.get_clear_chart()) {
                clearChart()
            }
        }, 1000)
    }
    render() {
        return (
            <div className="ChartContainer">
                <h2 className="ChartTitle" style={{ gridRowStart: 1 }}>
                    Real-time RTT (ms)
                </h2>
                <div id="RealTimeRTT" className="GridColumnSpan13" style={{ gridRowStart: 2}}></div>
                <h2 className="ChartTitle" style={{ gridRowStart: 3 }}>
                    Real-time Throughput (Mbps)
                </h2>
                {/*<div id="RealTimeThroughputSnd" className="GridColumnSpan12" style={{ gridRowStart: 4}}></div>*/}
                <div id="RealTimeThroughputRcv" className="GridColumnSpan13" style={{ gridRowStart: 4}}></div>
                <h2 className="ChartTitle" style={{ gridRowStart: 5 }}>
                    Time Average FCT
                </h2>
                <div id="TimeAverageFCT" className="GridColumnSpan13" style={{ gridRowStart: 6}}></div>
                <h2 className="ChartTitle" style={{ gridRowStart: 7 }}>
                    Time Average Slowdown
                </h2>
                <div id="TimeAverageSlowdown" className="GridColumnSpan13" style={{ gridRowStart: 8}}></div>
            </div>
        );
    }
}
