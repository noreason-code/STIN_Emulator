import {useState} from "react";
import "./style.css"
import {Card, Select, Input, Button, Modal, message, Progress, Space, Slider} from "antd"
import prefabs from "../satellite_prefabs.json"

export default function SateSet(props) {
    const state = {
        para_title: "配置星座参数",
        sel_default: "选择预设星座",
        track_height: "轨道高度（千米）",
        track_dip: "轨道倾角（度）",
        track_count: "轨道数目（条）",
        sate_density: "单轨卫星数（颗/轨）",
        phase_factor: "相位因子",
        button_string: "重建星座"
    }

    let rebuildInterval;

    const [track_height, set_track_height] = useState(500);
    const [track_dip_angle, set_track_dip_angle] = useState(50);
    const [track_count, set_track_count] = useState(2);
    const [satellite_density, set_satellite_density] = useState(2);
    const [phase_factor, set_phase_factor] = useState(0);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [isRebuildModalOpen, setIsRebuildModalOpen] = useState(false);
    const [isModalLoading, setModalLoading] = useState(false);
    const [processPercent, setProcessPercent] = useState(0);

    const selectChangeHandle = (value) => {
        console.log(`Selected: ${value}`)
        const prefab = prefabs[value];
        set_track_height(prefab["track_height"]);
        set_track_dip_angle(prefab["track_dip_angle"])
        set_track_count(prefab["track_count"])
        set_satellite_density(prefab["satellite_density"])
        set_phase_factor(prefab["phase_factor"])
    };

    const inputVerify = (content, description, pat) => {
        if (content.length === 0) {
            message.error(`请填写内容：${description}`).then();
            return false;
        }
        if (!pat.test(content)) {
            message.error(`格式错误：${description}`).then();
            return false;
        }
        return true;
    }

    const buttonOnClick = () => {
        const int_pat = /^\d+$/;
        const float_pat = /^\d+(\.\d+)?$/;
        if (
            inputVerify(track_height, state["track_height"], float_pat) &&
            inputVerify(track_dip_angle, state["track_dip"], float_pat) &&
            inputVerify(track_count, state["track_count"], int_pat) &&
            inputVerify(satellite_density, state["sate_density"], int_pat) &&
            inputVerify(phase_factor, state["phase_factor"], int_pat)
        ) {
            // setIsModalOpen(true);
            handleOk();
        }
    };

    const rebuildModalCancel = () => {
        if (processPercent < 99.999) {
            return;
        }
        setIsRebuildModalOpen(false);
    }

    const handleOk = () => {
        // setModalLoading(true);
        const sate_data = {
            "orbit_num": parseInt(track_count),
            "sat_num_per_orbit": parseInt(satellite_density),
            // "delay_satellite": 0,
            // "bandwidth_satellite": 10,
            // "loss_satellite": 0,
            // "delay_ground": 0,
            // "bandwidth_ground": 100,
            // "loss_ground": 0,
            // "create_ground_list":[0,1,2]
        };
        console.log(sate_data);
        props.notifier(sate_data, state.para_title)
    };

    const handleCancel = () => {
        setIsModalOpen(false);
    };

    const select_list = []
    for (let key in prefabs) {
        select_list.push({value: key, label: prefabs[key]['name']})
    }

    return (
        <div>
            <Card className={"sate_set_card"}>
                <Select className={"sate_prefab_select"}
                        defaultValue={state["sel_default"]}
                        style={{
                            width: 120,
                        }}
                        onChange={selectChangeHandle}
                        options={select_list}
                />
                <h2 style={{marginTop: "-20px"}}>{"\u00A0" + state["para_title"]}</h2>
                <div>
                    {state["track_height"]}
                    <Input
                        rootClassName={"sate_set_input"}
                        id={"track_height"}
                        value={track_height}
                        onChange={e => {
                            set_track_height(e.target.value)
                        }}
                        disabled={true}
                    />
                </div>
                <div>
                    {state["track_dip"]}
                    <Input
                        rootClassName={"sate_set_input"}
                        id={"track_dip_angle"}
                        value={track_dip_angle}
                        onChange={e => {
                            set_track_dip_angle(e.target.value)
                        }}
                        disabled={true}
                    />
                </div>
                <div>
                    {state["track_count"]}
                    <Input
                        rootClassName={"sate_set_input"}
                        id={"track_count"}
                        value={track_count}
                        onChange={e => {
                            set_track_count(e.target.value)
                        }}
                    />
                </div>
                <div>
                    {state["sate_density"]}
                    <Input
                        rootClassName={"sate_set_input"}
                        id={"satellite_density"}
                        value={satellite_density}
                        onChange={e => {
                            set_satellite_density(e.target.value)
                        }}
                    />
                </div>
                <div>
                    {state["phase_factor"]}
                    <Input
                        rootClassName={"sate_set_input"}
                        id={"phase_factor"}
                        value={phase_factor}
                        onChange={e => {
                            set_phase_factor(e.target.value)
                        }}
                        disabled={true}
                    />
                </div>
                <div>
                    <Button
                        className={"sate_set_button"}
                        onClick={buttonOnClick}>{state["button_string"]}
                    </Button>
                </div>
            </Card>
            <Modal
                title="重建星座"
                open={isModalOpen}
                onOk={handleOk}
                onCancel={handleCancel}
                footer={[
                    <Button key={"cancel"} onClick={handleCancel}>取消</Button>,
                    <Button key={"submit"} onClick={handleOk} loading={isModalLoading} type={"primary"}>确认</Button>
                ]}
            >
                <p>重建可能会消耗大量时间，请再次确认！</p>
                <p>{state["track_height"]}：{track_height}</p>
                <p>{state["track_dip"]}：{track_dip_angle}</p>
                <p>{state["track_count"]}：{track_count}</p>
                <p>{state["sate_density"]}：{satellite_density}</p>
                <p>{state["phase_factor"]}：{phase_factor}</p>
            </Modal>
            <Modal
                title="重建星座中"
                open={isRebuildModalOpen}
                onCancel={rebuildModalCancel}
                footer={[]}
            >
                <Space wrap>
                    <Progress type="line" percent={processPercent} size={[450, 20]} />
                </Space>
            </Modal>
        </div>
    )
}
