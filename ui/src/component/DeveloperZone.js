import {killConstellation} from "../axios"
import {Modal} from "antd";

export const dev_keys = {
    trigger_sider: ["xxx-01", "切换右侧边栏"],
    pause_chart: ["xxx-02", "切换加载图线"],
    clear_chart: ["xxx-03", "清空图线"],
    kill_star: ["xxx-04", "析构星座"],
    start_redraw: ["xxx-05", "强制开始重绘"],
    stop_redraw: ["xxx-06", "强制停止重绘"]
}

export function DeveloperZone(props) {
    switch (props.dev_key) {
        case dev_keys.trigger_sider[0]: {
            props.trig_collapse()
            break
        }
        case dev_keys.pause_chart[0]: {
            props.trig_chart_work()
            break
        }
        case dev_keys.clear_chart[0]: {
            props.set_clear_chart()
            break
        }
        case dev_keys.kill_star[0]: {
            props.set_flag("sateUpdate", false);
            killConstellation((resp) => {
                if (resp.code === 200) {
                    Modal.success({
                        title: "成功！",
                        content: resp.message,
                    })
                } else {
                    Modal.error({
                        title: "失败！",
                        content: `[${resp.code}] ${resp.message}`,
                    })
                }
            })
            break
        }
        case dev_keys.start_redraw[0]: {
            props.set_flag("sateUpdate", true);
            break
        }
        case dev_keys.stop_redraw[0]: {
            props.set_flag("sateUpdate", false);
            break
        }
        default: {
            console.log("Unexpected Key!")
            break
        }
    }
    props.set_key("")
}
