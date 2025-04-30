import {
    testPing,
    launchExperimentLongLive,
    launchExperimentFCT,
    terminateTransmissionExperiment
} from "./axios"
import {
    queryRTT,
    queryThroughput,
    queryFCT
} from "./axiosForChart";
import {message} from "antd";

export default class ExperimentManager {
    constructor(props) {
        console.log("Experiment Manager constructor!")
        this.clearSig = true  // 见 ChartsDrawer 中图标初始化的相关内容
        this.workFlag = false
        this.data = {
            "receiver_ground_index": 0,
            "sender_ground_index": 0,
            // "test_modal": 0,
            "test_duration": 0,
            // "trans_proto": "",
            // "reno_decrease_cwnd": 0,
            // "bbr_gain": 0,
            // "bbr_rtt": 0,
            // "bbr_unit1": 0,
            // "bbr_unit2": 0,
            // "cubic_rtt_scale": 0,
            // "cubic_decrease_cwnd": 0
        }
        this.transmission_pair = {
            "receiver_ground_index": 0,
            "sender_ground_index": 1,
        }
        this.transmission_protocol = {
            "cc": "BBR"
        }
    }

    getClear = () => {
        if (this.clearSig) {
            this.clearSig = false
            return true
        }
        return false
    }

    setClear = () => {
        this.clearSig = true
    }

    trigWork = () => {
        this.workFlag = !this.workFlag;
    }

    getWork = () => {
        return this.workFlag
    }

    setChartCallback = (fn) => {
        this.updateThroughput = fn["throughput"];
        this.updateRTT = fn["rtt"];
        this.updateFCT = fn["fct"];
        this.clearChart = fn["clear"];
    }

    startPingTest = () => {
        testPing(this.transmission_pair, (resp) => {
            // callback(resp["code"] === 200)
            console.log(resp)
        })
    }

    startLongLiveExperiment = (callback) => {
        this.workFlag = true;
        // 只向服务器端发通告，不产生其他副作用，回调函数仅仅是显示一个信息提示框（非模态）
        launchExperimentLongLive({...this.transmission_pair, "cc": this.transmission_protocol["cc"]},
            (resp) => {
                if (!callback(resp)) {
                    return
                }
                // 清理图线
                this.clearChart()
                // 获取吞吐
                setTimeout( () => {
                    // 定时器，每个一秒请求一次数据，直接由 axios 函数调用 updateCallback
                    this.interval_throughput = setInterval(
                        () => {
                            queryThroughput(
                                this.updateThroughput
                            )
                        }, 1000
                    )
                }, 11000);
                // 获取 RTT
                setTimeout(() => {
                    this.interval_rtt = setInterval(
                        () => {
                            queryRTT(
                                this.updateRTT
                            )
                        }, 1000
                    )
                }, 11500);
                // 定时关闭
                setTimeout(() => {
                    this.stopLongLiveExperiment()
                }, (this.data["test_duration"] + 12) * 1000)
            });
    }

    stopLongLiveExperiment = () => {
        this.workFlag = false;
        clearInterval(this.interval_throughput)
        clearInterval(this.interval_rtt)
        terminateTransmissionExperiment(
            (resp) => {
                console.log(resp)
                message.info("测试结束！\n" + JSON.stringify(resp)).then()
            }
        )
    }

    startFCT = (model, callback) => {
        this.workFlag = true;
        launchExperimentFCT(
            {
                ...this.transmission_pair,
                "time": this.data["test_duration"],
                "cc": this.transmission_protocol["cc"],
                "flow_type": model === 2 ? "campus" : model === 1 ? "CAIDA" : undefined
            },
            (resp) => {
                if (!callback(resp)) {
                    return
                }
                // 清理图线
                this.clearChart()
                // 获取 FCT
                setTimeout( () => {
                    this.interval_fct = setInterval(
                        () => {
                            queryFCT(
                                this.updateFCT
                            )
                        }, 2000
                    )
                }, 1000);
                // 定时关闭
                setTimeout(() => {
                    this.stopFCTExperiment()
                }, this.data["test_duration"] * 1000)
            });
    }

    stopFCTExperiment = () => {
        this.workFlag = false;
        clearInterval(this.interval_fct)
        message.info("测试结束！").then()
        // terminateTransmissionExperiment(
        //     (resp) => {
        //         console.log(resp)
        //     }
        // )
    }

    update = (data) => {
        this.data = {...this.data, ...data}
        console.log(this.data)
    }

    updateTransmissionPair = (data) => {
        this.transmission_pair = {...this.transmission_pair, ...data}
    }

    getTransmissionPair = () => {
        return this.transmission_pair
    }

    updateTransmissionProtocol = (data) => {
        this.transmission_protocol["cc"] = data
    }

    getTransmissionProtocol = () => {
        return this.transmission_protocol["cc"]
    }

}
