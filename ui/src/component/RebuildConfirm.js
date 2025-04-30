import {Descriptions, Modal, Button} from "antd";
import {useState} from "react";

export default function RebuildConfirm(props) {

    const state = {
        orbit_num: "轨道数目（轨）",
        sat_num_per_orbit: "单轨卫星数（颗/轨）",
        // delay_satellite: "星间链路延迟（ms）",
        bandwidth_satellite: "星间链路带宽（Mbps）",
        link_failure_rate: "星间链路故障率",
        // delay_ground: "星地链路延迟（ms）",
        bandwidth_ground: "星地链路带宽（Mbps）",
        loss_ground: "星地链路误码率",
        switch_cost: "星间链路切换开销 （ms）",
        create_ground_list: "启用地面站编号"
    }

    const [isModalOpen, setIsModalOpen] = useState(true);
    const [isModalLoading, setModalLoading] = useState(false);

    const data = props.get_data();

    console.log(data);

    let items = []

    Object.entries(data).forEach(([key, value]) => {
        if (key in state) {
            items.push(
                <Descriptions.Item label={state[key]}>{value.toString()}</Descriptions.Item>
            )
        }
    })

    console.log(items);

    const close_key = () => {
        props.set_key("")
    }

    const handleOk = () => {
        setModalLoading(true);
        props.rebuild_axios(
            data,
            (resp) => {
                setModalLoading(false);
                setIsModalOpen(false);
                if (resp.code === 200) {
                    Modal.success({
                        title: "重建成功！",
                        content: resp.message,
                        onOk: close_key,
                        onCancel: close_key
                    })
                    props.set_flag("sateUpdate", true)
                } else {
                    Modal.error({
                        title: "重建失败！",
                        content: `[${resp.code}] ${resp.message}`,
                        onOk: close_key,
                        onCancel: close_key
                    })
                }
            }
        )
    }

    const handleCancel = () => {
        if (!isModalLoading) {
            setIsModalOpen(false);
        }
        props.set_key("")
    }

    return (
        <div>
            <Modal
                title="重建星座"
                width={850}
                open={isModalOpen}
                onOk={handleOk}
                onCancel={handleCancel}
                footer={[
                    <Button key={"cancel"} onClick={handleCancel}>取消</Button>,
                    <Button key={"submit"} onClick={handleOk} loading={isModalLoading} type={"primary"}>确认</Button>
                ]}
            >
                <p>重建可能会消耗大量时间，请再次确认！</p>
                <Descriptions bordered>
                    {items}
                </Descriptions>
            </Modal>
        </div>
    )
}