import React from 'react';
import {Button, notification, Space} from 'antd';

export default class RebuildNotification {
    constructor(props) {
        console.log("Rebuild Notifier constructor!")
        this.rebuild_data = {
            "orbit_num": 6,
            "bandwidth_satellite": 400,
            "link_failure_rate": 0.0,
            "sat_num_per_orbit": 11,
            "bandwidth_ground": 300,
            "loss_ground": 0,
            "loss_satellite": 0,
            "switch_cost": 0,
            "create_ground_list": []
        };
    }

    key = ""

    close = () => {
        console.log(
            'Notification was closed.',
        );
    };

    // confirmRebuild = () => {
    //     console.log(this.rebuild_data); // TODO
    //     this.opened = false;
    //     notification.destroy(this.key);
    // }

    openNotification = (title) => {
        this.key = `open${Date.now()}`;
        // const btn = (
        //     <Space>
        //         <Button type="primary" size="small" onClick={() => this.confirmRebuild()}>
        //             确认
        //         </Button>
        //     </Space>
        // );
        notification.open({
            message: `星座重建尚未进行！(${title})`,
            description:
                `您的修改已经记录，请前往“确认重建”标签进行重建！`,
            // btn: btn,
            key: this.key,
            onClose: this.close,
            duration: 3
        });
    };

    update = (data, title) => {
        this.rebuild_data = {...this.rebuild_data, ...data};
        this.openNotification(title);
    };

    get_data = () => {
        return this.rebuild_data
    }

    get_ground_index = () => {
        return this.rebuild_data.create_ground_list
    }
}