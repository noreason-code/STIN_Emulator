import {Group} from "three";
import para from '../../parameters.json'
import {GLTFLoader} from "three/examples/jsm/loaders/GLTFLoader";
import {DRACOLoader} from "three/examples/jsm/loaders/DRACOLoader";
import earth_3d from "../../3d_object/earth.glb";

export const initEarth = (group: Group) => {
  const loader = new GLTFLoader();
  const dracoLoader = new DRACOLoader();
  dracoLoader.setDecoderPath('/draco/');
  dracoLoader.preload(earth_3d);
  loader.setDRACOLoader(dracoLoader);

  loader.load(earth_3d, (gltf) => {
    let scale_num = 0.205 * para.earth_radius;
    gltf.scene.scale.set(scale_num, scale_num, scale_num);
    gltf.scene.rotateY(1.57);
    //gltf.scene.rotateX(1);
    gltf.scene.name = 'earth';
    group.add(gltf.scene);
  }, undefined, (err) => {
    console.log(err);
  });
}