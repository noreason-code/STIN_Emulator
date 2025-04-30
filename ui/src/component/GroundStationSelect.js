import React, { useState } from 'react';
import { Select, Space ,Modal} from 'antd';
import GroundStations from "../groundPositionData.json"

const MyComponent = (props) => {
  const [selectedValues, setSelectedValues] = useState([]); // 初始选中的数据
  const options = Object.keys(GroundStations).map((siteName) => {
      const index = parseInt(Object.keys(GroundStations).indexOf(siteName), 10)
      return {
          label: index.toString() + " - " + siteName,
          value: index,
      }
    }
  )
  const handleChange = (value) => {
    value = value.sort(function(a, b) {return a - b})
    // console.log(`选定的值：`, value);
    setSelectedValues(value);
    props.notifier({
      "create_ground_list": value
    }, "地面站配置");
    props.setIndex(value)
    // props.setGroundStation(
    //     value,
    //     (data) => {
    //         if (data.status === "Ok") {
    //             Modal.success({title: "配置成功！"});
    //         } else {
    //             Modal.error({title: "配置失败！", content: data.reason});
    //         }
    //     }
    // )
  };

  return (
    <Space style={{ width: '100%' }} direction="vertical">
      <Select
        mode="multiple"
        allowClear
        style={{ width: '50%',color: 'white' }}
        placeholder="Please select"
        value={selectedValues} // 使用value而不是defaultValue
        onChange={handleChange}
        options={options}
      />
    </Space>
  );
};

export default MyComponent;
