
"use strict";

let SyncModeSetGear = require('./SyncModeSetGear.js');
let IntersectionStatus = require('./IntersectionStatus.js');
let SyncModeCtrlCmd = require('./SyncModeCtrlCmd.js');
let SetTrafficLight = require('./SetTrafficLight.js');
let ManipulatorControl = require('./ManipulatorControl.js');
let RadarDetections = require('./RadarDetections.js');
let SyncModeCmd = require('./SyncModeCmd.js');
let NpcGhostCmd = require('./NpcGhostCmd.js');
let Lamps = require('./Lamps.js');
let FaultInjection_Tire = require('./FaultInjection_Tire.js');
let NpcGhostInfo = require('./NpcGhostInfo.js');
let MoraiSimProcHandle = require('./MoraiSimProcHandle.js');
let EgoVehicleStatusExtended = require('./EgoVehicleStatusExtended.js');
let RobotOutput = require('./RobotOutput.js');
let Conveyor = require('./Conveyor.js');
let MultiEgoSetting = require('./MultiEgoSetting.js');
let EventInfo = require('./EventInfo.js');
let VehicleCollisionData = require('./VehicleCollisionData.js');
let Transforms = require('./Transforms.js');
let MultiPlayEventResponse = require('./MultiPlayEventResponse.js');
let MoraiTLInfo = require('./MoraiTLInfo.js');
let SVADC = require('./SVADC.js');
let DillyCmdResponse = require('./DillyCmdResponse.js');
let ReplayInfo = require('./ReplayInfo.js');
let SkidSteer6wUGVCtrlCmd = require('./SkidSteer6wUGVCtrlCmd.js');
let SyncModeInfo = require('./SyncModeInfo.js');
let VelocityCmd = require('./VelocityCmd.js');
let ERP42Info = require('./ERP42Info.js');
let DdCtrlCmd = require('./DdCtrlCmd.js');
let SkateboardCtrlCmd = require('./SkateboardCtrlCmd.js');
let ObjectStatus = require('./ObjectStatus.js');
let SyncModeRemoveObject = require('./SyncModeRemoveObject.js');
let SyncModeCmdResponse = require('./SyncModeCmdResponse.js');
let MoraiTLIndex = require('./MoraiTLIndex.js');
let SyncModeAddObject = require('./SyncModeAddObject.js');
let SensorPosControl = require('./SensorPosControl.js');
let GeoVector3Message = require('./GeoVector3Message.js');
let SkateboardStatus = require('./SkateboardStatus.js');
let WoowaDillyStatus = require('./WoowaDillyStatus.js');
let FaultInjection_Response = require('./FaultInjection_Response.js');
let ShipCtrlCmd = require('./ShipCtrlCmd.js');
let GhostMessage = require('./GhostMessage.js');
let GVStateCmd = require('./GVStateCmd.js');
let ObjectStatusExtended = require('./ObjectStatusExtended.js');
let WheelControl = require('./WheelControl.js');
let DillyCmd = require('./DillyCmd.js');
let TOF = require('./TOF.js');
let RadarDetection = require('./RadarDetection.js');
let MoraiSrvResponse = require('./MoraiSrvResponse.js');
let IntscnTL = require('./IntscnTL.js');
let Obstacle = require('./Obstacle.js');
let SkidSteer6wUGVStatus = require('./SkidSteer6wUGVStatus.js');
let IntersectionControl = require('./IntersectionControl.js');
let PRCtrlCmd = require('./PRCtrlCmd.js');
let TrafficLight = require('./TrafficLight.js');
let EgoVehicleStatus = require('./EgoVehicleStatus.js');
let RobotState = require('./RobotState.js');
let CollisionData = require('./CollisionData.js');
let CMDConveyor = require('./CMDConveyor.js');
let SyncModeScenarioLoad = require('./SyncModeScenarioLoad.js');
let ScenarioLoad = require('./ScenarioLoad.js');
let GVDirectCmd = require('./GVDirectCmd.js');
let ExternalForce = require('./ExternalForce.js');
let PREvent = require('./PREvent.js');
let FaultStatusInfo_Vehicle = require('./FaultStatusInfo_Vehicle.js');
let FaultStatusInfo_Sensor = require('./FaultStatusInfo_Sensor.js');
let PRStatus = require('./PRStatus.js');
let WaitForTickResponse = require('./WaitForTickResponse.js');
let GetTrafficLightStatus = require('./GetTrafficLightStatus.js');
let Obstacles = require('./Obstacles.js');
let VehicleCollision = require('./VehicleCollision.js');
let WaitForTick = require('./WaitForTick.js');
let ShipState = require('./ShipState.js');
let MapSpec = require('./MapSpec.js');
let CtrlCmd = require('./CtrlCmd.js');
let GPSMessage = require('./GPSMessage.js');
let UGVServeSkidCtrlCmd = require('./UGVServeSkidCtrlCmd.js');
let SyncModeResultResponse = require('./SyncModeResultResponse.js');
let FaultInjection_Controller = require('./FaultInjection_Controller.js');
let VehicleSpec = require('./VehicleSpec.js');
let EgoDdVehicleStatus = require('./EgoDdVehicleStatus.js');
let ObjectStatusList = require('./ObjectStatusList.js');
let FaultInjection_Sensor = require('./FaultInjection_Sensor.js');
let MoraiSimProcStatus = require('./MoraiSimProcStatus.js');
let FaultStatusInfo = require('./FaultStatusInfo.js');
let SaveSensorData = require('./SaveSensorData.js');
let FaultStatusInfo_Overall = require('./FaultStatusInfo_Overall.js');
let MultiPlayEventRequest = require('./MultiPlayEventRequest.js');
let MapSpecIndex = require('./MapSpecIndex.js');
let VehicleSpecIndex = require('./VehicleSpecIndex.js');
let ObjectStatusListExtended = require('./ObjectStatusListExtended.js');

module.exports = {
  SyncModeSetGear: SyncModeSetGear,
  IntersectionStatus: IntersectionStatus,
  SyncModeCtrlCmd: SyncModeCtrlCmd,
  SetTrafficLight: SetTrafficLight,
  ManipulatorControl: ManipulatorControl,
  RadarDetections: RadarDetections,
  SyncModeCmd: SyncModeCmd,
  NpcGhostCmd: NpcGhostCmd,
  Lamps: Lamps,
  FaultInjection_Tire: FaultInjection_Tire,
  NpcGhostInfo: NpcGhostInfo,
  MoraiSimProcHandle: MoraiSimProcHandle,
  EgoVehicleStatusExtended: EgoVehicleStatusExtended,
  RobotOutput: RobotOutput,
  Conveyor: Conveyor,
  MultiEgoSetting: MultiEgoSetting,
  EventInfo: EventInfo,
  VehicleCollisionData: VehicleCollisionData,
  Transforms: Transforms,
  MultiPlayEventResponse: MultiPlayEventResponse,
  MoraiTLInfo: MoraiTLInfo,
  SVADC: SVADC,
  DillyCmdResponse: DillyCmdResponse,
  ReplayInfo: ReplayInfo,
  SkidSteer6wUGVCtrlCmd: SkidSteer6wUGVCtrlCmd,
  SyncModeInfo: SyncModeInfo,
  VelocityCmd: VelocityCmd,
  ERP42Info: ERP42Info,
  DdCtrlCmd: DdCtrlCmd,
  SkateboardCtrlCmd: SkateboardCtrlCmd,
  ObjectStatus: ObjectStatus,
  SyncModeRemoveObject: SyncModeRemoveObject,
  SyncModeCmdResponse: SyncModeCmdResponse,
  MoraiTLIndex: MoraiTLIndex,
  SyncModeAddObject: SyncModeAddObject,
  SensorPosControl: SensorPosControl,
  GeoVector3Message: GeoVector3Message,
  SkateboardStatus: SkateboardStatus,
  WoowaDillyStatus: WoowaDillyStatus,
  FaultInjection_Response: FaultInjection_Response,
  ShipCtrlCmd: ShipCtrlCmd,
  GhostMessage: GhostMessage,
  GVStateCmd: GVStateCmd,
  ObjectStatusExtended: ObjectStatusExtended,
  WheelControl: WheelControl,
  DillyCmd: DillyCmd,
  TOF: TOF,
  RadarDetection: RadarDetection,
  MoraiSrvResponse: MoraiSrvResponse,
  IntscnTL: IntscnTL,
  Obstacle: Obstacle,
  SkidSteer6wUGVStatus: SkidSteer6wUGVStatus,
  IntersectionControl: IntersectionControl,
  PRCtrlCmd: PRCtrlCmd,
  TrafficLight: TrafficLight,
  EgoVehicleStatus: EgoVehicleStatus,
  RobotState: RobotState,
  CollisionData: CollisionData,
  CMDConveyor: CMDConveyor,
  SyncModeScenarioLoad: SyncModeScenarioLoad,
  ScenarioLoad: ScenarioLoad,
  GVDirectCmd: GVDirectCmd,
  ExternalForce: ExternalForce,
  PREvent: PREvent,
  FaultStatusInfo_Vehicle: FaultStatusInfo_Vehicle,
  FaultStatusInfo_Sensor: FaultStatusInfo_Sensor,
  PRStatus: PRStatus,
  WaitForTickResponse: WaitForTickResponse,
  GetTrafficLightStatus: GetTrafficLightStatus,
  Obstacles: Obstacles,
  VehicleCollision: VehicleCollision,
  WaitForTick: WaitForTick,
  ShipState: ShipState,
  MapSpec: MapSpec,
  CtrlCmd: CtrlCmd,
  GPSMessage: GPSMessage,
  UGVServeSkidCtrlCmd: UGVServeSkidCtrlCmd,
  SyncModeResultResponse: SyncModeResultResponse,
  FaultInjection_Controller: FaultInjection_Controller,
  VehicleSpec: VehicleSpec,
  EgoDdVehicleStatus: EgoDdVehicleStatus,
  ObjectStatusList: ObjectStatusList,
  FaultInjection_Sensor: FaultInjection_Sensor,
  MoraiSimProcStatus: MoraiSimProcStatus,
  FaultStatusInfo: FaultStatusInfo,
  SaveSensorData: SaveSensorData,
  FaultStatusInfo_Overall: FaultStatusInfo_Overall,
  MultiPlayEventRequest: MultiPlayEventRequest,
  MapSpecIndex: MapSpecIndex,
  VehicleSpecIndex: VehicleSpecIndex,
  ObjectStatusListExtended: ObjectStatusListExtended,
};
