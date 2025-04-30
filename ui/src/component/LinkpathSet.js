import {useState} from "react";
import "./style.css"
import {Card, Select, Input, Button, Modal, message, Progress, Space, Slider} from "antd"

export default function LinkpathSet(props) {
    const state = {
        para_title: "配置链路参数",
        para_subtitle1: "星间链路参数",
        bandwidth1: "星间链路带宽（Mbps）",
        link_failure_rate: "星间链路故障率（%）",
        sat_delay: "星间链路延迟（ms）",
        para_subtitle2: "星地链路参数",
        bandwidth2: "星地链路带宽（Mbps）",
        miscode_rate: "星地链路误码率（%）",
        ground_delay: "星地链路延迟（ms）",
        para_subtitle3: "其他参数",
        packloss_rate: "星地链路丢包率（%）*",
        button_string: "重建星座",
        switch_cost: "切换开销（ms）"
    }

    const [bandwidth1, set_bandwidth1] = useState(10);
    const [failure_rate, set_failure_rate] = useState(0);
    const [bandwidth2, set_bandwidth2] = useState(10);
    const [miscode_rate, set_miscode_rate] = useState(0);
    const [switch_cost, set_switch_cost] = useState(0);
    const [sat_delay, set_sat_delay] = useState(0);
    const [ground_delay, set_ground_delay] = useState(0);
    const [isLoading, setIsLoading] = useState(false);

    const buttonOnClick = () => {
        const link_data = {
            // "orbit_num": track_count,
            // "sat_num_per_orbit": satellite_density,
            // "delay_satellite": sat_delay,
            "bandwidth_satellite": parseInt(bandwidth1),
            "link_failure_rate": parseInt(failure_rate) / 100,
            // "delay_ground": ground_delay,
            "bandwidth_ground": parseInt(bandwidth2),
            "loss_ground": parseInt(miscode_rate) / 100,
            "switch_cost": parseInt(switch_cost)
            // "create_ground_list": [0,1,2]
        };

        console.log(link_data);
        props.notifier(link_data, state.para_title);
    }

    return (
        <div>
            <Card className={"link_set_card"}>
                {/*<h2 style={{marginTop: "-20px"}}>{"\u00A0" + state["para_title"]}</h2>*/}
                <h3 style={{marginTop: "0px"}}>{"\u00A0" + state["para_subtitle1"]}</h3>
                <div>
                    {state["bandwidth1"]}
                    <Input
                        rootClassName={"sate_set_input"}
                        id={"bandwidth1"}
                        value={bandwidth1}
                        onChange={e => {
                            set_bandwidth1(e.target.value)
                        }}
                    />
                </div>
                <div>
                    {state["link_failure_rate"]}
                    <Input
                        rootClassName={"sate_set_input"}
                        id={"link_failure_rate"}
                        value={failure_rate}
                        onChange={e => {
                            set_failure_rate(e.target.value)
                        }}
                    />
                </div>
                <div>
                    {state["switch_cost"]}
                    <Input
                        rootClassName={"sate_set_input"}
                        id={"switch_cost"}
                        value={switch_cost}
                        onChange={e => {
                            set_switch_cost(e.target.value)
                        }}
                    />
                </div>
                <div>
                    <h3 style={{marginTop: "0px"}}>{"\u00A0" + state["para_subtitle2"]}</h3>
                    <div>
                        {state["bandwidth2"]}
                        <Input
                            rootClassName={"sate_set_input"}
                            id={"bandwidth2"}
                            value={bandwidth2}
                            onChange={e => {
                                set_bandwidth2(e.target.value)
                            }}
                        />
                    </div>
                    <div>
                        {state["miscode_rate"]}
                        <Input
                            rootClassName={"sate_set_input"}
                            id={"miscode_rate"}
                            value={miscode_rate}
                            onChange={e => {
                                set_miscode_rate(e.target.value)
                            }}
                        />
                    </div>
                </div>
                <Button
                    className={"sate_set_button"}
                    onClick={buttonOnClick}
                    loading={isLoading}
                >
                    {state["button_string"]}
                </Button>
            </Card>
        </div>
    )
}