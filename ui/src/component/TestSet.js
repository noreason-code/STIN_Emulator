import React from 'react';
import {useState} from "react";
import "./style.css"
import { Select, Space ,Card, Input, Button, Modal, message, Progress, Slider, Cascader, Radio} from 'antd';
export default function TestSet(props) {
    const state={
        flow_model: "互联网流模型",
        test_duration: "测试时长(s)"
    }
    const [flow_model, set_flow_model] = useState("");
    const [test_duration, set_test_duration] = useState("");
    const [start_loading, set_start_loading] = useState(false)

    const model_list=[
        {value: 1, label: "CAIDA 数据集"},
        {value: 2, label: "BUAA 数据集"},
        // {value: 3, label: "自定义流大小分布"},
        {value: 4, label: "Long-lived 流量"},
    ];

    const handlerStartTest = (resp) => {
        set_start_loading(false)
        if (resp.code === 200) {
            message.success(`启动测试成功（${resp.message}）`).then()
            return true
        } else {
            message.error(`启动测试失败（[${resp.code}] ${resp.message}）`).then()
            return false
        }
    }

    const handlerStartClick = () => {
        set_start_loading(true)
        // props.ping()
        // if (ping) {
        //     message.success("Ping test is Ok!").then()
        if (flow_model === 4) {
            props.start_long_live(handlerStartTest)
        } else if (flow_model === 2 || flow_model === 1) {
            props.start_fct(flow_model, handlerStartTest)
        } else {
            set_start_loading(false)
            message.error("Unknown Test Modal: " + flow_model).then()
        }
        // } else {
        //     Modal.error({
        //         title: "Ping test",
        //         content: "Ping test error! View the console for more detailed information. The test will not be launched."
        //     })
        //     set_start_loading(false)
        // }

    }

    return(
        <Card className={"test_set_card"} style={{left:"200px",top:"-280px",width:"250px"}} >
            <Space direction="vertical" size="large" style={{ display: 'flex' }}>
                <div>
                    <h2 style={{marginTop: "-20px"}}>{"\u00A0" + state["flow_model"]}</h2>
                    <Select className={"flow_model_select"}
                            //defaultValue={state["sel_default"]}
                            style={{
                                width: 150,
                            }}
                            onChange={(value) => {
                                set_flow_model(value)
                                props.update({ test_modal: value })
                            }}
                            options={model_list}
                    />
                </div>
                <div>
                    <h2 style={{marginTop: "-20px"}}>{"\u00A0" + state["test_duration"]}</h2>
                    <div>
                        <Input
                            rootClassName={"duration_set_input"}
                            style={{
                                width: 150,
                            }}
                            id={"test_duration"}
                            value={test_duration}
                            onChange={(e) => {
                                const value = parseInt(e.target.value)
                                set_test_duration(value)
                                props.update({ test_duration: value })
                            }}
                        />
                    </div>
                </div>
                <div>
                    <Space>
                        <Button loading={start_loading} onClick={handlerStartClick}>开始测试</Button>
                        {/*<Button>展示结果</Button>*/}
                    </Space>
                </div>
            </Space>
        </Card>
    )
}