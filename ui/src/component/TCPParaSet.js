import React from 'react';
import {useState} from "react";
import { Select ,Card, Input, Button, message} from 'antd';
export default function TCPParaSet(props){
    const state = {
        para_title:"传输控制协议配置",
        TCP_select:"请选择控制协议",
        Reno_decrease_cwnd:"Reno 窗口减小系数",
        BBR_gain:"BBR cwnd增益系数",
        BBR_RTT:"BBR 往返时延持续时间（ms）",
        BBR_UNIT1:"BBR 发送速率增益系数",
        BBR_UNIT2:"BBR 发送速率排空系数",
        CUBIC_RTT_Scale:"CUBIC cwnd增益系数",
        CUBIC_decrease_cwnd:"CUBIC 窗口减小参数",
        button_string:"确认",
    }

    const TCP_list=[
        {value: "Reno", label: "Reno 协议"},
        {value: "BBR", label: "BBR 协议"},
        {value: "CUBIC", label: "CUBIC 协议"},
    ];

    const [TCP_select, set_TCP_select] = useState(props.init_protocol);
    const [Reno_decrease_cwnd, set_Reno_decrease_cwnd] = useState(0.5);
    const [BBR_gain, set_BBR_gain] = useState(10);
    const [BBR_RTT, set_BBR_RTT] = useState(200);
    const [BBR_UNIT1, set_BBR_UNIT1] = useState(1.25);
    const [BBR_UNIT2, set_BBR_UNIT2] = useState(0.75);
    const [CUBIC_RTT_Scale, set_CUBIC_RTT_Scale] = useState(0.4);
    const [CUBIC_decrease_cwnd, set_CUBIC_decrease_cwnd] = useState(0.5);

    const buttonOnClick = () => {
        props.update(TCP_select)
        message.info("Chosen protocol: " + TCP_select).then()
    }

    const handleSelect = (value) => {
        console.log(value)
        set_TCP_select(value)
    }

    return (
        <div>
            <Card className={"TCPParaSet"}>
                <h2 style={{marginTop: "-20px"}}>{"\u00A0" + state["para_title"]}</h2>
                <div>
                    {state["TCP_select"]}
                    <Select className={"TCP_select"}
                            style={{
                                width: 150,
                            }}
                            onChange={handleSelect}
                            options={TCP_list}
                            defaultValue={TCP_select}
                    />
                    {(() => {
                            switch (TCP_select) {
                                case "Reno":
                                    return (
                                        <div>
                                            {state["Reno_decrease_cwnd"]}
                                            <Input
                                                rootClassName={"TCP_para_set_input"}
                                                id={"Reno_decrease_cwnd"}
                                                value={Reno_decrease_cwnd}
                                                onChange={e => {
                                                    set_Reno_decrease_cwnd(e.target.value)
                                                }}
                                            />
                                        </div>
                                    )
                                case "BBR":
                                    return (
                                        <div>
                                        <div>
                                            {state["BBR_gain"]}
                                            <Input
                                                rootClassName={"TCP_para_set_input"}
                                                id={"BBR_gain"}
                                                value={BBR_gain}
                                                onChange={e => {
                                                    set_BBR_gain(e.target.value)
                                                }}
                                            />
                                        </div>
                                        <div>
                                            {state["BBR_RTT"]}
                                            <Input
                                                rootClassName={"TCP_para_set_input"}
                                                id={"BBR_RTT"}
                                                value={BBR_RTT}
                                                onChange={e => {
                                                    set_BBR_RTT(e.target.value)
                                                }}
                                            />
                                        </div>
                                        <div>
                                            {state["BBR_UNIT1"]}
                                            <Input
                                                rootClassName={"TCP_para_set_input"}
                                                id={"BBR_UNIT1"}
                                                value={BBR_UNIT1}
                                                onChange={e => {
                                                    set_BBR_UNIT1(e.target.value)
                                                }}
                                            />
                                        </div>
                                        <div>
                                            {state["BBR_UNIT2"]}
                                            <Input
                                                rootClassName={"TCP_para_set_input"}
                                                id={"BBR_UNIT2"}
                                                value={BBR_UNIT2}
                                                onChange={e => {
                                                    set_BBR_UNIT2(e.target.value)
                                                }}
                                            />
                                        </div>
                                        </div>
                                    )
                                case "CUBIC":
                                    return (
                                    <div>
                                    <div>
                                        {state["CUBIC_RTT_Scale"]}
                                        <Input
                                            rootClassName={"TCP_para_set_input"}
                                            id={"CUBIC_RTT_Scale"}
                                            value={CUBIC_RTT_Scale}
                                            onChange={e => {
                                                set_CUBIC_RTT_Scale(e.target.value)
                                            }}
                                        />
                                    </div>
                                    <div>
                                        {state["CUBIC_decrease_cwnd"]}
                                        <Input
                                            rootClassName={"TCP_para_set_input"}
                                            id={"CUBIC_decrease_cwnd"}
                                            value={CUBIC_decrease_cwnd}
                                            onChange={e => {
                                                set_CUBIC_decrease_cwnd(e.target.value)
                                            }}
                                        />
                                    </div>
                                    </div>
                                )
                                default:
                                    console.log(`Unexpected select: ${TCP_select}`)
                                    break;
                            }
                        }
                    )()}
                </div>
                <br/>
                <div>
                    <Button onClick={buttonOnClick}>确认</Button>
                </div>
            </Card>
        </div>
    )
}