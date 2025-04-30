import React, { Component } from 'react';
import {useState} from "react";
import { Select, Space ,Card, Input, Button, Modal, message, Progress, Slider} from 'antd';
const handleChange = (value) => {
  console.log(`selected ${value}`);
};
const GroundStations = {
    "Nome_AK": {"height": -892948, "lat": 64.5035, "long": -165.428305},
    "Kenansville_FL": {"height": -892948, "lat": 27.876006, "long": -81.030486},
    "St_John": {"height": -892948, "lat": 47.560854, "long": -52.775388},
    "Broken_Hill_NSW": {"height": -892948, "lat": -31.998258, "long": 141.441058},
    "Pimba_SA": {"height": -892948, "lat": -31.250747, "long": 136.801335},
    "Boorawa_NSW": {"height": -892948, "lat": -34.462093, "long": 148.705734},
    "Wagin_WA": {"height": -892948, "lat": -33.308268, "long": 117.343372},
    "Awarua": {"height": -892948, "lat": -46.528889, "long": 168.378611},
    "Cromwell": {"height": -892948, "lat": -45.059722, "long": 169.206111},
    "Hinds": {"height": -892948, "lat": -43.921944, "long": 171.89},
    "Clevedon": {"height": -892948, "lat": -36.989722, "long": 175.055278},
    "Te_Hana": {"height": -892948, "lat": -36.236944, "long": 174.512222},
    "Puwera": {"height": -892948, "lat": -35.793333, "long": 174.300278},
    "Cobargo_NSW": {"height": -892948, "lat": -36.38861, "long": 149.89139},
    "Torrumbarry_VIC": {"height": -892948, "lat": -36.025227, "long": 144.50012},
    "Ki_Ki_SA": {"height": -892948, "lat": -35.57156, "long": 139.81749},
    "Cataby_WA": {"height": -892948, "lat": -30.848289, "long": 115.61951},
    "Merredin_WA": {"height": -892948, "lat": -31.494875, "long": 118.27777},
    "Bogantungan_QLD": {"height": -892948, "lat": -23.648001, "long": 147.292890},
    "Calrossie_NSW": {"height": -892948, "lat": -29.057781, "long": 150.040010},
    "Springbrook_Creek_NSW": {"height": -892948, "lat": -30.439794, "long": 149.683847},
    "Bulla_Bulling_WA": {"height": -892948, "lat": -31.029747, "long": 120.819820},
    "Villenave": {"height": -892948, "lat": 44.780952, "long": -0.537323},
    "Gravelines": {"height": -892948, "lat": 50.989632, "long": 2.157900},
    "Goonhilly": {"height": -892948, "lat": 50.049530, "long": -5.179298},
    "Chalfont_Grove": {"height": -892948, "lat": 51.614596, "long": -0.574415},
    "Usingen": {"height": -892948, "lat": 50.219917, "long": 8.470778},
    "Aerzen": {"height": -892948, "lat": 52.060991, "long": 9.328222},
    "Isle_of_Man": {"height": -892948, "lat": 54.139038, "long": -4.497211},
    "Elfordstown": {"height": -892948, "lat": 51.953111, "long": -8.174333},
    "Punta_Arenas": {"height": -892948, "lat": -52.938100, "long": -70.857222},
    "Pudahuel": {"height": -892948, "lat": -33.392703, "long": -70.883119},
    "Caldera": {"height": -892948, "lat": -27.019700, "long": -70.787800},
    "Coquimbo": {"height": -892948, "lat": -29.999400, "long": -71.258600},
    "Talca": {"height": -892948, "lat": -35.556000, "long": -71.356800},
    "Puerto_Saavedra": {"height": -892948, "lat": -38.814800, "long": -73.397300},
    "Puerto_Montt": {"height": -892948, "lat": -41.486600, "long": -73.022000},
    "Sambro_Creek": {"height": -892948, "lat": 44.465490, "long": -63.613420},
    "La_Baie_QC": {"height": -892948, "lat": 48.302890, "long": -70.916040},
    "Canyonleigh": {"height": -892948, "lat": -34.589043, "long": 150.188390},
    "Tea_Gardens": {"height": -892948, "lat": -32.593193, "long": 152.104200},
    "Koonwarra": {"height": -892948, "lat": -38.518120, "long": 145.951450},
    "Anakie": {"height": -892948, "lat": -37.953169, "long": 144.328172},
    "Warra": {"height": -892948, "lat": -36.908108, "long": 150.892062},
    "Toonpan": {"height": -892948, "lat": -19.518612, "long": 146.873640},
    "Willows": {"height": -892948, "lat": -22.666677, "long": 147.502550},
    "Wola_Krobowska": {"height": -892948, "lat": 51.864222, "long": 20.921083},
    "Frederick_MD": {"height": -892948, "lat": 39.396970, "long": -777.436640},
    "Molokai_HI": {"height": -892948, "lat": 21.109330, "long": -157.063940},
    "Columbus_OH": {"height": -892948, "lat": 40.061000, "long": -82.760770},
    "Elbert_CO": {"height": -892948, "lat": 39.292520, "long": 104.504750},
    "North_Bend_WA": {"height": -892948, "lat": 47.482440, "long": -121.761300},
    "Brewster_WA": {"height": -892948, "lat": 48.148610, "long": -119.701130},
    "Saint_Senier": {"height": -892948, "lat": 48.576400, "long": -1.310700},
    "Gebze": {"height": -892948, "lat": 40.7887, "long": 29.5095},
    "Madrid": {"height": -892948, "lat": 40.16758, "long": -3.28686},
    "Lbi": {"height": -892948, "lat": 38.6307, "long": -0.5447},
    "Lepe": {"height": -892948, "lat": 37.2572, "long": -7.2033},
    "Foggia": {"height": -892948, "lat": 41.507306, "long": 15.585439},
    "Petrosino": {"height": -892948, "lat": 37.711, "long": 12.4879},
    "Lacchiarella": {"height": -892948, "lat": 45.3207, "long": 9.1886},
    "Conrad_MT": {"height": -892948, "lat": 48.203306, "long": -111.945278},
    "Loring_ME": {"height": -892948, "lat": 46.914917, "long": -67.919528},
    "Redmond_WA": {"height": -892948, "lat": 47.694194, "long": -122.032139},
    "Greenville_PA": {"height": -892948, "lat": 41.433566, "long": -80.333222},
    "Merrillan_WI": {"height": -892948, "lat": 44.406333, "long": -90.814278},
    "Kalama_WA": {"height": -892948, "lat": 46.038972, "long": -122.808222},
    "Hawthorne_CA": {"height": -892948, "lat": 33.9175, "long": -118.328111},
    "Arbuckle_CA": {"height": -892948, "lat": 39.057, "long": -122.06},
    "Beekmantown_NY": {"height": -892948, "lat": 44.789972, "long": -73.48},
    "Charleston_OR": {"height": -892948, "lat": 43.248417, "long": -124.381194},
    "Panaca_NV": {"height": -892948, "lat": 37.783639, "long": -114.692694},
    "Boca_Chica_TX": {"height": -892948, "lat": 25.990694, "long": -97.18275},
    "McGregor_TX": {"height": -892948, "lat": 31.4004917, "long": -97.438139},
    "Litchfield_CT": {"height": -892948, "lat": 41.545028, "long": -73.354028},
    "Warren_MO": {"height": -892948, "lat": 38.635167, "long": -91.116028},
    "Nemaha_NE": {"height": -892948, "lat": 40.333667, "long": -95.815278},
    "Manistique_MI": {"height": -892948, "lat": 45.908611, "long": -86.483583},
    "Slope_County_ND": {"height": -892948, "lat": 46.408389, "long": -103.114583},
    "Los_Angeles_CA": {"height": -892948, "lat": 34.604028, "long": -117.454361},
    "Cass_County_ND": {"height": -892948, "lat": 47.151694, "long": -97.408889},
    "Sanderson_TX": {"height": -892948, "lat": 30.194, "long": -102.89},
    "Springer_OK": {"height": -892948, "lat": 34.2685, "long": -97.213167},
    "Hitterdal_MN": {"height": -892948, "lat": 46.978917, "long": -96.258028},
    "Tionesta_CA": {"height": -892948, "lat": 41.644, "long": -121.329972},
    "Butte_MT": {"height": -892948, "lat": 45.924056, "long": -112.513194},
    "Colburn_ID": {"height": -892948, "lat": 48.34525, "long": -116.439333},
    "Baxley_GA": {"height": -892948, "lat": 31.682167, "long": -82.268972},
    "Robertsdale_AL": {"height": -892948, "lat": 30.567, "long": -87.646},
    "Roll_AZ": {"height": -892948, "lat": 32.8155, "long": -113.798056},
    "Prosser_WA": {"height": -892948, "lat": 46.127278, "long": -119.684305},
    "Vernon_UT": {"height": -892948, "lat": 40.076222, "long": -112.354722},
    "Inman_KS": {"height": -892948, "lat": 38.229, "long": -97.921972},
    "Evanston_WY": {"height": -892948, "lat": 41.0925, "long": -110.842611},
    "Punta_Gorda_FL": {"height": -892948, "lat": 27.019667, "long": -81.762028},
    "Tracy_City_TN": {"height": -892948, "lat": 35.19725, "long": -85.666},
    "Kuparuk_AK": {"height": -892948, "lat": 70.317667, "long": -148.941194},
    "Gaffney_SC": {"height": -892948, "lat": 34.985306, "long": -81.733083},
    "Robbins_CA": {"height": -892948, "lat": 38.875, "long": -121.707055},
    "Wise_NC": {"height": -892948, "lat": 36.470639, "long": -78.173389},
    "Mandale_NC": {"height": -892948, "lat": 35.895361, "long": -79.224889},
    "Dumas_TX": {"height": -892948, "lat": 35.807972, "long": -102.031861},
    "Hamshire_TX": {"height": -892948, "lat": 29.859861, "long": -94.312333},
    "Marcell_MN": {"height": -892948, "lat": 47.593167, "long": -933.692528},
    "Lockport_NY": {"height": -892948, "lat": 43.166566, "long": -78.755111},
    "Hillman_MI": {"height": -892948, "lat": 45.07325, "long": -82.900417},
    "Lawrence_KS": {"height": -892948, "lat": 39.013889, "long": -95.149389},
    "Norcross_GA": {"height": -892948, "lat": 33.954972, "long": -84.197972},
    "Fort_Lauderdale": {"height": -892948, "lat": 26.190861, "long": -80.193083},
    "Broadview_IL": {"height": -892948, "lat": 41.854889, "long": -87.858889},
    "Sullivan_ME": {"height": -892948, "lat": 44.530972, "long": -68.224},
    "Lunenburg_VT": {"height": -892948, "lat": 44.412028, "long": -71.7318833},
    "Ketchikan_AK": {"height": -892948, "lat": 55.314611, "long": -131.585694},
    "Rolette_ND": {"height": -892948, "lat": 48.660361, "long": -99.810528},
    "Fairbanks_AK": {"height": -892948, "lat": 64.805167, "long": -147.500222},
    "New_Braunfels_TX": {"height": -892948, "lat": 29.784056, "long": -98.050778}
    };
const pair_list = Object.keys(GroundStations).map((siteName) => {
    const index = parseInt(Object.keys(GroundStations).indexOf(siteName), 10);
    return {
          label: index.toString() + " - " + siteName,
          value: index,
      }
});
class TransmissionPair extends Component {
    
    constructor(props) {
        super(props);
        this.state = {
            para_title1:"传输对配置",
            transmission_pair1:"传输对1",
            transmission_pair2:"传输对2",
            transmission_pair3:"传输对3",
            pair1_sender: props.init_pairs["sender_ground_index"],
            pair1_receiver: props.init_pairs["receiver_ground_index"],
            pair2_sender:"Sender",
            pair2_receiver:"Receiver",
            pair3_sender:"Sender",
            pair3_receiver:"Receiver",
            loading: false,
        }
        this.update = props.update
      }
      
    onChangePair1Sender = (value) => {
        this.setState({pair1_sender: value});
        this.update({ sender_ground_index: value})
    }
    onChangePair1Receiver = (value) => {
        this.setState({pair1_receiver: value});
        this.update({ receiver_ground_index: value})
    }
    onChangePair2Sender = (value) => {
        this.setState({pair2_sender: value});
    }
    onChangePair2Receiver = (value) => {
        this.setState({pair2_receiver: value});
    }
    onChangePair3Sender = (value) => {
        this.setState({pair3_sender: value});
    }
    onChangePair3Receiver = (value) => {
        this.setState({pair3_receiver: value});
    }

    
    render() {
        return (
            <div>
                <Card className={"TCP_set_card"} style = {{left:"200px",top:"-280px",width:"200px"}}>
                    <h2 style={{marginTop: "-20px"}}>{"\u00A0" + this.state["para_title1"]}</h2> 
                    <div>
                    <div>{this.state["transmission_pair1"]}</div>
                        <Select className={"sender1_select"}
                                defaultValue={this.state.pair1_sender}
                                style={{
                                    width: 120,
                                }}
                                onChange = {this.onChangePair1Sender}
                                options={pair_list}
                        />
                    </div>
                    <div>
                        <Select className={"receiver1_select"}
                                defaultValue={this.state.pair1_receiver}
                                style={{
                                    width: 120,
                                }}
                                onChange = {this.onChangePair1Receiver}
                                options={pair_list}
                        />
                    </div>
                    <div>
                    <div>{this.state["transmission_pair2"]}</div>
                        <Select className={"sender2_select"}
                                defaultValue={this.state.pair2_sender}
                                style={{
                                    width: 120
                                }}
                                onChange = {this.onChangePair2Sender}
                                options={pair_list}
                                disabled={true}
                        />
                    </div>
                    <div>
                        <Select className={"receiver2_select"}
                                defaultValue={this.state.pair2_receiver}
                                style={{
                                    width: 120,
                                }}
                                onChange = {this.onChangePair2Receiver}
                                options={pair_list}
                                disabled={true}
                        />
                    </div>
                    <div>
                        <div>{this.state["transmission_pair3"]}</div>
                        
                        <Select className={"sender3_select"}
                                defaultValue={this.state.pair3_sender}
                                style={{
                                    width: 120,
                                }}
                                onChange = {this.onChangePair3Sender}
                                options={pair_list}
                                disabled={true}
                        />
                    </div>
                    <div>
                        <Select className={"receiver3_select"}
                                defaultValue={this.state.pair3_receiver}
                                style={{
                                    width: 120,
                                }}
                                onChange = {this.onChangePair3Receiver}
                                options={pair_list}
                                disabled={true}
                        />
                    </div>
                </Card>
            </div>
        )
    }
    
} 
export default TransmissionPair;
                 