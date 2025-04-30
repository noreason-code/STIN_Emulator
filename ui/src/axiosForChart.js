import axios from "axios";
import {message} from "antd"
import para from "./parameters.json"

export const queryThroughput = (callback) => {
    axios.get(para.url + "/api/get_throughput").then(
        (response) => {
            console.log("Get Throughput: " + JSON.stringify(response.data))
            if (response.data["code"] === 200) {
                callback(response.data["real_time_throughput"])
            } else {
                callback(0)
            }
        }
    ).catch(
        (error) => {
            console.log("Get experiment data error (Throughput): " + error)
            message.error("Get experiment data error (Throughput): " + error).then()
        }
    )
}

export const queryRTT = (callback) => {
    axios.get(para.url + "/api/get_rtt").then(
        (response) => {
            console.log("Get RTT: " + JSON.stringify(response.data))
            if (response.data["code"] === 200) {
                callback(response.data["real_time_rtt"])
            } else {
                callback(0)
            }
        }
    ).catch(
        (error) => {
            console.log("Get experiment data error (RTT): " + error)
            message.error("Get experiment data error (RTT): " + error).then()
        }
    )
}

export const queryFCT = (callback) => {
    axios.get(para.url + "/api/get_FCT").then(
        (response) => {
            console.log("Get FCT: " + JSON.stringify(response.data))
            if (response.data["code"] === 200) {
                callback(response.data["FCT"])
            } else {
                callback(0)
            }
        }
    ).catch(
        (error) => {
            console.log("Get experiment data error (FCT): " + error)
            message.error("Get experiment data error (FCT): " + error).then()
        }
    )
}