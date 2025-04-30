import {Group} from 'three';
import {GroundStation} from "../object/GroundStation";
import {Label} from "../object/Label";
import {sateLocation2xyz} from "./sateLocation2xyz";

export const addGroundStations = (groundPositions, group, builtPosition, pickedGroundIndex) => {
  /**
   * @description 根据地面站的位置信息，添加地面站
   * @param groundPositions {Array} 地面站的位置信息
   * @param group {Group} 场景组
   * @param builtPosition 后端建立的地面站
   */
  const groundGroup = new Group();
  const labelGroup = new Group();

  // 全部地面站
  let idx = -1
  for (let key in groundPositions) {
    const groundPosition = groundPositions[key];
    // console.log(key);
    idx++;
    // console.log(idx, key, pickedGroundIndex.indexOf(idx))
    const groundStation = GroundStation(groundPosition, false, pickedGroundIndex.indexOf(idx) > -1);
    groundStation.name = key;
    groundGroup.add(groundStation);

    const xyz = sateLocation2xyz(groundPosition);
    const label = Label(Object.keys(groundPositions).indexOf(key).toString(), xyz, 0.15);
    label.name = key;
    labelGroup.add(label);
  }

  // 后端启用地面站（视觉上覆盖）
  for (let key in builtPosition) {
    const groundPosition = builtPosition[key];
    // console.log(key);
    const groundStation = GroundStation(groundPosition, true, false);
    groundStation.name = key;
    groundGroup.add(groundStation);
  }

  groundGroup.name = 'groundGroup';
  group.add(groundGroup);

  labelGroup.name = 'groundLabelGroup';
  group.add(labelGroup);
};