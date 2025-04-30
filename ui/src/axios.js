import para from "./parameters.json";
import axios from "axios";
import {message} from "antd";

export const getSatelliteStatus = (callback) => {
    axios.get(para.monitor_url + '/api/satellite/status').then(
        (response) => {
            console.log(response.data.data);
            callback(response.data.data);
        }).catch((error) => {
        console.log("get locations error:" + error);
    })
}

export const getSatelliteList = (callback) => {
    axios.get(para.monitor_url + '/api/satellite/list').then(
        (response) => {
            console.log(response.data.data);
            callback(response.data.data);
        }).catch((error) => {
        console.log("get locations error:" + error);
    })
}

export const getSatelliteInterfaces = (callback) => {
    axios.get(para.monitor_url + '/api/satellite/interfaces').then(
        (response) => {
            console.log(response.data.data);
            callback(response.data.data);
        }).catch((error) => {
        console.log("get interfaces error:" + error);
    })
}

export const getCommandTraceroute = (src_id, dst_ip, callback) => {
    axios.get(para.monitor_url + '/api/command/traceroute?src_id=' + src_id + '&dst_ip=' + dst_ip).then(
        (response) => {
            console.log(response.data.data);
            callback(response.data.data);
        }).catch((error) => {
        console.error("get route path error:" + error);
        message.error("不存在路由路径！").then();
    })
}

export const getGroundPosition = (callback) => {
    axios.get(para.monitor_url + '/api/ground/position').then(
        (response) => {
            console.log(response.data.data);
            callback(response.data.data);
        }).catch((error) => {
        console.log("get ground position error:" + error);
    })
}

export const getGroundConnection = (callback) => {
    axios.get(para.monitor_url + '/api/ground/connection').then(
        (response) => {
            console.log(response.data.data);
            callback(response.data.data);
        }).catch((error) => {
        console.log("get ground status error:" + error);
    })
}

/**
 * 调用服务器的 api 设置卫星参数
 * @param sate_data 卫星参数的 json 数据
 * @param callback 处理返回的信息，设置成功与否
 */
export const setSatelliteParameter = (sate_data, callback) => {
    axios({
        method: "post",
        url: para.url + '/api/intial/constellation',
        data: JSON.stringify({...sate_data, ...{ "delay_ground": 0, "delay_satellite": 0, "user_list": [0,1,2,3,4,5,6,7,8,9], "user_ground_connection": [[0,0], [1,1], [2,2], [3,3], [4,4], [5,5], [6,6], [7,7], [8,8], [9,9]] }}),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        (response) => {
            console.log(response.data);
            callback(response.data);
        }
    ).catch(
        (error) => {
            console.log("Set satellite parameter error: " + error);
            callback({code: "-1", message: "Http response error!"});
        }
    )
}

/**
 * 也许很玄学的 Ping 的测试！
 * @param data 填传输对即可
 * @param callback
 */
export const testPing = (data, callback) => {
    axios({
        method: "post",
        url: para.url + "/api/ping_test",
        data: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        (response) => {
            console.log(response.data)
            callback(response.data)
        }
    ).catch(
        (error) => {
            console.log("Ping test error: " + error);
            callback({code: "-1", message: "Http response error!"})
        }
    )
}

/**
 * 向服务器发送测试配置，启动测试（长流，吞吐与 RTT）
 * @param data
 * @param callback
 */
export const launchExperimentLongLive = (data, callback) => {
    axios({
        method: "post",
        url: para.url + "/api/strat_throughput_and_rtt",
        data: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        (response) => {
            console.log(response.data)
            callback(response.data)
        }
    ).catch(
        (error) => {
            console.log("Launch experiment error: " + error);
            callback({code: "-1", message: "Http response error!"})
        }
    )
}

export const launchExperimentFCT = (data, callback) => {
    axios({
        method: "post",
        url: para.url + "/api/start_FCT",
        data: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        (response) => {
            console.log(response.data)
            callback(response.data)
        }
    ).catch(
        (error) => {
            console.log("Launch experiment error: " + error);
            callback({code: "-1", message: "Http response error!"})
        }
    )
}

/**
 * 向服务器发送终止测试的消息
 * @param callback
 */
export const terminateTransmissionExperiment = (callback) => {
    axios.post(para.url + "/api/socket_stop").then(
        (response) => {
            console.log(response.data)
            callback(response.data)
        }
    ).catch(
        (error) => {
            console.log("Terminate experiment error: " + error);
            callback({code: "-1", message: "Http response error!"})
        }
    )
}

/**
 * 杀死星座！
 * @param callback
 */
export const killConstellation = (callback) => {
    axios.post(para.url + "/api/stop_and_kill_constellation").then(
        (response) => {
            console.log(response.data)
            callback(response.data)
        }
    ).catch(
        (error) => {
            console.log("Kill Constellation error: " + error)
            callback({code: "-1", message: "Http response error!"})
        }
    )
}

/**
 *
 * @param callback
 * @deprecated
 */
export const queryExperimentData = (callback) => {
    axios.get(para.url + "/api/socket_get").then(
        (response) => {
            console.log(response.data)
            if (response.data["code"] === 200) {
                callback([response.data["real_time_rtt"], response.data["real_time_throughput_sender"]])
            }
        }
    ).catch(
        (error) => {
            console.log("Get experiment data error: " + error)
        }
    )
}

/**
 * 向服务器发送链路配置
 * @param link_data 链路参数的 json 数据
 * @param callback 回调函数
 * @deprecated
 */
export const setSatelliteLinkage = (link_data, callback) => {
    // json content:
    // {
    //      "failure_rate": failure_rate,
    //      "packloss_rate": packloss_rate,
    //      "delay": delay,
    //      "bandwidth": bandwidth,
    // }
    axios({
        method: "post",
        url: para.url + '/api/initial/linkpath',
        data: JSON.stringify(link_data),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        (response) => {
            console.log(response.data);
            callback(response.data);
        }
    ).catch(
        (error) => {
            console.log("Set link parameter error:" + error);
            callback({status: "error"});
        }
    )
}

/**
 * 向服务器询问重建进度
 * @param callback 回调函数，对进度条的进度进行设置
 * @deprecated
 */
export const getSatelliteRebuildProcess = (callback) => {
    axios.get(para.url + "/api/initial/process/").then(
        (response) => {
            callback(response.data);
        }
    ).catch(
        (error) => {
            console.log("Get satellite rebuild process error:" + error);
        }
    )
}

/**
 *
 * @param groundStationData
 * @param callback
 * @deprecated
 */
export const setGroundStation = (groundStationData, callback) => {
    axios({
        method: "post",
        url: para.url + '/api/initial/constellation',
        data: JSON.stringify(groundStationData),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        (response) => {
            console.log(response.data);
            callback(response.data);
        }
    ).catch(
        (error) => {
            console.log("Set ground station parameter error:" + error);
            callback({status: "error"});
        }
    )
}

/**
 *
 * @param groundStationData
 * @param callback
 * @deprecated
 */
export const setTransmissionPair = (groundStationData, callback) => {
    axios({
        method: "post",
        url: para.url + '/api/initial/constellation',
        data: JSON.stringify(groundStationData),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        (response) => {
            console.log(response.data);
            callback(response.data);
        }
    ).catch(
        (error) => {
            console.log("Set transmissionPair parameter error:" + error);
            callback({status: "error"});
        }
    )
}

/**
 *
 * @param TCPPara
 * @param callback
 * @deprecated
 */
export const setTCPPara = (TCPPara, callback) => {
    axios({
        method: "post",
        url: para.url + '/api/initial/constellation',
        data: JSON.stringify(TCPPara),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        (response) => {
            console.log(response.data);
            callback(response.data);
        }
    ).catch(
        (error) => {
            console.log("Set TCP parameter error:" + error);
            callback({status: "error"});
        }
    )
}

/**
 *
 * @param flowModel
 * @param callback
 * @deprecated
 */
export const setFlowModel = (flowModel, callback) => {
    axios({
        method: "post",
        url: para.url + '/api/initial/constellation',
        data: JSON.stringify(flowModel),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        (response) => {
            console.log(response.data);
            callback(response.data);
        }
    ).catch(
        (error) => {
            console.log("Set ground station parameter error:" + error);
            callback({status: "error"});
        }
    )
}

/**
 *
 * @param flowDuration
 * @param callback
 * @deprecated
 */
export const setFlowDuration = (flowDuration, callback) => {
    axios({
        method: "post",
        url: para.url + '/api/initial/constellation',
        data: JSON.stringify(flowDuration),
        headers: {
            'Content-Type': 'application/json'
        }
    }).then(
        (response) => {
            console.log(response.data);
            callback(response.data);
        }
    ).catch(
        (error) => {
            console.log("Set ground station parameter error:" + error);
            callback({status: "error"});
        }
    )
}