import React, {useEffect, useState} from "react";
import './App.css'
import Model from './model/model.js'

import LinkSet from "./component/LinkSet";
import SatePara from "./component/SatePara";
import RoutePath from "./component/RoutePath";
import TransmitFile from "./component/TransmitFile";
import SateSet from "./component/SateSet"
import LinkPathSet from "./component/LinkpathSet"
import GroundStationSelect from "./component/GroundStationSelect"
import RebuildConfirm from "./component/RebuildConfirm";
import {dev_keys, DeveloperZone} from "./component/DeveloperZone";
import TestSet from "./component/TestSet"
import TransmissionPair from "./component/TransmissionPair";
import TCPParaSet from "./component/TCPParaSet";

import RebuildNotification from "./rebuildNotification";
import ExperimentManager from "./experimentManager";

import {Layout, Menu} from "antd";
import logo from './img/logo.png'
import Sider from "antd/es/layout/Sider";
import {
    ApartmentOutlined,
    ApiOutlined,
    BarChartOutlined,
    BlockOutlined,
    SettingOutlined,
    CheckOutlined,
    HomeOutlined,
    FunctionOutlined
} from "@ant-design/icons"
import {Content} from "antd/es/layout/layout";

import {
    getSatelliteStatus,
    getSatelliteList,
    getSatelliteInterfaces,
    getCommandTraceroute,
    getGroundPosition,
    getGroundConnection,
    setSatelliteParameter,
    launchExperimentLongLive
} from "./axios";

import GroundStation  from "./groundPositionData.json";
import ChatsDrawer from "./component/ChatsDrawer";

const items = [
    {
        key: '5',
        icon: <SettingOutlined />,
        label: '星座配置',
    },
    {
        key: '6',
        icon: <ApiOutlined />,
        label: '链路配置',
    },
    {
        key: '7',
        icon: <HomeOutlined />,
        label: '地面站配置',
    },
    {
        key: 'rebuild',
        icon: <CheckOutlined />,
        label: '确认重建',
    },
    {
        key: '8',
        icon: <SettingOutlined />,
        label: '传输对配置',
    },
    {
        key: '9',
        icon: <SettingOutlined />,
        label: '传输控制协议',
    },
    {
        key: '10',
        icon: <SettingOutlined />,
        label: '测试配置',
    },
    {
        key: 'xxx',
        icon: <FunctionOutlined />,
        label: '调试功能',
        children: [
            {
                key: dev_keys.trigger_sider[0],
                label: dev_keys.trigger_sider[1]
            },
            {
                key: dev_keys.pause_chart[0],
                label: dev_keys.pause_chart[1]
            },
            {
                key: dev_keys.clear_chart[0],
                label: dev_keys.clear_chart[1]
            },
            {
                key: dev_keys.kill_star[0],
                label: dev_keys.kill_star[1]
            },
            {
                key: dev_keys.start_redraw[0],
                label: dev_keys.start_redraw[1]
            },
            {
                key: dev_keys.stop_redraw[0],
                label: dev_keys.stop_redraw[1]
            }
        ]
    },
    // {
    //     key: '1',
    //     icon: <BarChartOutlined/>,
    //     label: '卫星参数',
    // },
    // {
    //     key: '2',
    //     icon: <ApartmentOutlined/>,
    //     label: '显示路由路径',
    // },
    // {
    //     key: '4',
    //     icon: <BlockOutlined/>,
    //     label: '文件传输测试',
    // },
    // {
    //     key: '3',
    //     icon: <ApiOutlined/>,
    //     label: '连接设置',
    // }
];

//fake data
// const mySateConnections = {
//     node_0:["node_2","node_2","node_2"],
//     node_1:["node_0","node_0","node_3","node_0","node_0","node_3","node_0","node_0","node_3"],
//     node_2:["node_3","node_3","node_3","node_3","node_3","node_3"]
// };
//
// const myInterfaces = {
//     node_0:[
//         {ip:"172.18.0.9",dst_id:"node_2"},
//         {ip:"172.18.0.19",dst_id:"node_1"},
//         {ip:"172.18.0.1",dst_id:"node_1"}
//     ],
//     node_1:[
//         {ip:"172.18.0.17",dst_id:"node_0"},
//         {ip:"172.18.0.3",dst_id:"node_0"},
//         {ip:"172.18.0.25",dst_id:"node_3"}
//     ],
//     node_2:[
//         {ip:"172.18.0.11",dst_id:"node_0"},
//         {ip:"172.18.0.43",dst_id:"node_3"},
//         {ip:"172.18.0.33",dst_id:"node_3"}
//     ],
//     node_3:[
//         {ip:"172.18.0.27",dst_id:"node_1"},
//         {ip:"172.18.0.41",dst_id:"node_2"},
//         {ip:"172.18.0.35",dst_id:"node_2"}
//     ]
// };
//
// const myGroundPosition = GroundStation
// const mySateLocations = {
//     node_0:{
//         height:1478314,
//         lat:1.4903,
//         long:0.6565,
//         open:false
//     },
//     node_1:{
//         height:1493230,
//         lat:-1.4905,
//         long:-2.4850,
//         open:false
//     },
//     node_2:{
//         height:1478310,
//         lat:1.4885,
//         long:2.2273,
//         open:false
//     },
//     node_3:{
//         height:1493234,
//         lat:-1.4916,
//         long:-0.9140,
//         open:false
//     }
// };
//
// const myGroundConnections = {
// };

const updateNotification = new RebuildNotification();
const experimentManager = new ExperimentManager();

let chartSiderCollapsed = false;
const trigCollapsed = () => {
    chartSiderCollapsed = !chartSiderCollapsed
}


const App = () => {
    const [sateLocations, setSateLocations] = useState({});
    const [sateConnections, setSateConnections] = useState({});
    const [groundPosition, setGroundPosition] = useState({});  // [经度，纬度] 后端返回的地面站
    const [pickedPosition, setPickedPosition] = useState([]);  // 前端选择的地面站编号列表
    const [groundConnections, setGroundConnections] = useState({});
    const [interfaces, setInterfaces] = useState({});
    const [routePath, setRoutePath] = useState([]);
    const [sateParaNodeId, setSateParaNodeId] = useState("node_0");  // 默认选择的卫星是Sat_0
    const [key, setKey] = useState('');
    const [flags, setFlags] = useState({
        "connect": true,
        "longLine": true,
        "label": true,
        "sateUpdate": false,
    });

    useEffect(() => {
        if (!flags["sateUpdate"]) {
            return () => {};
        }
        getSatelliteList((data) => {
            setSateConnections(data);
        });
        getSatelliteInterfaces((data) => {
            setInterfaces(data);
        });
        getGroundPosition((data) => {
            setGroundPosition(data);
        });
        getSatelliteStatus((data) => {
            // console.log("setSateLocations!")
            // console.log(data)
            setSateLocations(data);
        });
        getGroundConnection((data) => {
            setGroundConnections(data);
        });

        // 添加定时器，每秒获取一次卫星位置，地面站连接情况
        const interval = setInterval(() => {
            if (!flags["sateUpdate"]) {
                return;
            }
            getSatelliteStatus((data) => {
              setSateLocations(data);
            });
            getGroundConnection((data) => {
                setGroundConnections(data);
            });
        }, 1000);

        // 页面关闭时删除定时器
        return () => {
            console.log("Interval Killed!")
            clearInterval(interval);
        }
      }, [flags]);

    const getSatePara = (node_id) => {
        let all_node = [];
        for (let key in sateLocations) {
            all_node.push(key);
        }
        return {
            "all_node": all_node,
            "location": sateLocations[node_id],
            "connections": interfaces[node_id],
        }
    }

    const getAllRoute = () => {
        let all_node = [];
        for (let key in sateLocations) {
            all_node.push(key);
        }
        return {
            "all_node": all_node,
            "interfaces": interfaces,
        }
    }

    const getRoutePath = (src_id, dst_ip) => {
        getCommandTraceroute(src_id, dst_ip, (data) => {
            setRoutePath(data);
        });
    }

    // const updateNotification = RebuildNotification();
    // console.log(myGroundPosition)

    const updateFlag = (str, bool) => {
        setFlags({...flags, ...{[str]: bool}});
        console.log(flags)
    }

    return (
        <Layout style={{
            height: '100%',
            width: '100%',
            overflow:"hidden"  // 解决溢出问题
        }}>
            <Sider trigger={null} collapsible collapsed={false}>
                <img className={"logo"} src={logo} alt={"logo"}/>
                <Menu className={"menu"}
                      theme="dark"
                      mode="inline"
                      defaultSelectedKeys={key}
                      items={items}
                      onClick={(item) => {
                          if (key === item.key) {
                              setKey("");
                          } else {
                              setKey(item.key);
                          }
                      }}
                />
                <div className="data_table">
                    {
                        (key === '5') ?
                            <SateSet
                                notifier={updateNotification.update}
                            /> :
                        (key === '6') ?
                            <LinkPathSet
                                notifier={updateNotification.update}
                            /> :
                        (key === '7') ?
                            <GroundStationSelect
                                notifier={updateNotification.update}
                                setIndex={setPickedPosition}
                            /> :
                        (key === 'rebuild') ?
                            <RebuildConfirm
                                get_data={updateNotification.get_data}
                                rebuild_axios={setSatelliteParameter}
                                set_key={setKey}
                                set_flag={updateFlag}
                            /> :
                        (key === '8') ?
                            <TransmissionPair
                                update={experimentManager.updateTransmissionPair}
                                init_pairs={experimentManager.getTransmissionPair()}
                            /> :
                        (key === '9') ?
                            <TCPParaSet
                                update={experimentManager.updateTransmissionProtocol}
                                init_protocol={experimentManager.getTransmissionProtocol()}
                            /> :
                        (key === '10') ?
                            <TestSet
                                update={experimentManager.update}
                                ping={experimentManager.startPingTest}
                                start_long_live={experimentManager.startLongLiveExperiment}
                                start_fct={experimentManager.startFCT}
                            /> :
                        (key.startsWith('xxx')) ?
                            <DeveloperZone
                                dev_key={key}
                                trig_collapse={trigCollapsed}
                                trig_chart_work={experimentManager.trigWork}
                                set_clear_chart={experimentManager.setClear}
                                set_key={setKey}
                                set_flag={updateFlag}
                            /> :
                            undefined
                    }
                </div>
            </Sider>
            <Layout className="site-layout">
                <Content style={{
                    height: '100%',
                    width: '100%',
                    backgroundColor: '#1d1d1d'
                }}>
                    <Model sateLocations={sateLocations}
                           sateConnections={sateConnections}
                           groundPosition={GroundStation}
                           chosenGround={groundPosition}
                           groundConnections={groundConnections}
                           pickedGroundStation={pickedPosition}
                           routePath={routePath}
                           selected_sate={sateParaNodeId}
                           flags={flags}
                           displayPara={(node_id) => {
                               setSateParaNodeId(node_id);
                               setKey("1");
                           }}/>
                </Content>
            </Layout>
            <Sider collapsible={true} collapsedWidth={0} width={500} trigger={null} collapsed={chartSiderCollapsed}>
                <ChatsDrawer
                    get_chart_work={experimentManager.getWork}
                    get_clear_chart={experimentManager.getClear}
                    set_chart_callback={experimentManager.setChartCallback}
                />
            </Sider>
        </Layout>
    )
}

export default App;
