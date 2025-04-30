import { Group, BufferGeometry, Vector3, PointsMaterial, Points, TextureLoader, DoubleSide, MeshBasicMaterial, PlaneGeometry, Mesh } from "three";
import para from "../../parameters.json";
import wave_img from "../../img/wave.png";

export const GroundStation = (position, is_built, is_chosen) => {
  /**
   * @description 根据地面位置初始化地面站
   * @param position {long: float, lat: float} 地面站位置
   * @param is_built 是否选中（由后端确定）
   * @param is_chosen 是否选中（由前端确定）
   * @return Group 地面站模型组
   */
  const group = new Group();
  const rad = para.earth_radius+3;
  const theta = Math.PI / 2 - position.lat;
  const phi = -position.long;
  const x = rad * Math.sin(theta) * Math.cos(phi);
  const y = rad * Math.cos(theta);
  const z = rad * Math.sin(theta) * Math.sin(phi);

  // 调整点的高度
  //const yAdjusted = (Math.abs(y) + 6)*(y/Math.abs(y));

  // 添加一个简单的黄色点作为地面站图标
  const pointGeometry = new BufferGeometry().setFromPoints([new Vector3(x, y, z)]);
  const pointMaterial = new PointsMaterial({
    color: (is_built ? 0xEE0000 : is_chosen ? 0x66CCFF : 0xFFFF00),
    size: (is_built ? 4 : is_chosen ? 3 : 1)
  });
  const point = new Points(pointGeometry, pointMaterial);
  group.add(point);

  // 添加波纹效果
  // group.add(wave(x , y , z ));

  return group;
};

// const wave = (x, y, z) => {
//   const plane = new PlaneGeometry(1, 1);
//   const texture = new TextureLoader().load(wave_img);
//   const material = new MeshBasicMaterial({
//     color: 0x22ffcc,
//     map: texture,
//     transparent: true,
//     opacity: 1,
//     side: DoubleSide,
//     depthWrite: false,
//   });
//
//   const wave_mesh = new Mesh(plane, material);
//   wave_mesh.position.set(x, y, z);
//   const gs_normal_vec = new Vector3(x, y, z).normalize();
//   const mesh_normal_vec = new Vector3(0, 0, 1);
//   wave_mesh.quaternion.setFromUnitVectors(mesh_normal_vec, gs_normal_vec);
//   wave_mesh.size = 10;
//   wave_mesh._s = Math.random() + 1.0;
//
//   wave_mesh.name = "wave";
//   return wave_mesh;
// };

