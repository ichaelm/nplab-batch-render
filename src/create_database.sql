CREATE TABLE Scenes(
  sceneID INTEGER PRIMARY KEY,
  scene VARCHAR(255) UNIQUE NOT NULL
);

CREATE UNIQUE INDEX idx_Scenes_scene ON Scenes(scene);

CREATE TABLE CameraTargets(
  cameraTargetID INTEGER PRIMARY KEY,
  sceneID INTEGER NOT NULL,
  camera UNSIGNED BIG INT NOT NULL,
  target UNSIGNED BIG INT NOT NULL,
  FOREIGN KEY(sceneID) REFERENCES Scenes(sceneID),
  UNIQUE(sceneID, camera, target)
);

CREATE INDEX idx_CameraTargets_sceneID ON CameraTargets(sceneID);

CREATE TABLE Configs(
  configID INTEGER PRIMARY KEY,
  numTraces UNSIGNED INT NOT NULL,
  numFrames UNSIGNED INT NOT NULL
);

CREATE TABLE FrameInfo(
  frameID INTEGER PRIMARY KEY,
  cameraTargetID INTEGER NOT NULL,
  configID INTEGER NOT NULL,
  trace UNSIGNED INT NOT NULL,
  frame UNSIGNED INT NOT NULL,
  hasMXS BOOL NOT NULL,
  MXSLastModified DATETIME,
  MXSHash VARCHAR(255),
  hasImage BOOL NOT NULL,
  imageLastModified DATETIME,
  imageHash VARCHAR(255),
  FOREIGN KEY(cameraTargetID) REFERENCES CameraTargets(cameraTargetID),
  FOREIGN KEY(configID) REFERENCES Configs(configID),
  UNIQUE(cameraTargetID, configID, trace, frame)
);

CREATE INDEX idx_FrameInfo_cameraTargetID ON FrameInfo(cameraTargetID);
CREATE INDEX idx_FrameInfo_configID ON FrameInfo(configID);
CREATE INDEX idx_FrameInfo_hasMXS ON FrameInfo(hasMXS);
CREATE INDEX idx_FrameInfo_hasImage ON FrameInfo(hasImage);
CREATE INDEX idx_FrameInfo_cameraTargetID_configID ON FrameInfo(cameraTargetID, configID);
--CREATE INDEX idx_FrameInfo_cameraTargetID_configID_trace ON FrameInfo(cameraTargetID, configID, trace);
CREATE UNIQUE INDEX idx_FrameInfo_cameraTargetID_configID_trace_frame ON FrameInfo(cameraTargetID, configID, trace, frame);
--CREATE INDEX idx_FrameInfo_configID_trace ON FrameInfo(configID, trace);
--CREATE INDEX idx_FrameInfo_configID_trace_frame ON FrameInfo(configID, trace, frame);


--CREATE INDEX idx_FrameInfo_cameraTargetID_configID_hasMXS ON FrameInfo(cameraTargetID, configID, hasMXS);
--CREATE INDEX idx_FrameInfo_cameraTargetID_configID_trace_hasMXS ON FrameInfo(cameraTargetID, configID, trace, hasMXS);
--CREATE INDEX idx_FrameInfo_cameraTargetID_configID_trace_frame_hasMXS ON FrameInfo(cameraTargetID, configID, trace, frame, hasMXS);
--CREATE INDEX idx_FrameInfo_configID_hasMXS ON FrameInfo(configID, hasMXS);
--CREATE INDEX idx_FrameInfo_configID_trace_hasMXS ON FrameInfo(configID, trace, hasMXS);
--CREATE INDEX idx_FrameInfo_configID_trace_frame_hasMXS ON FrameInfo(configID, trace, frame, hasMXS);

--CREATE INDEX idx_FrameInfo_cameraTargetID_configID_hasImage ON FrameInfo(cameraTargetID, configID, hasImage);
--CREATE INDEX idx_FrameInfo_cameraTargetID_configID_trace_hasImage ON FrameInfo(cameraTargetID, configID, trace, hasImage);
--CREATE INDEX idx_FrameInfo_cameraTargetID_configID_trace_frame_hasImage ON FrameInfo(cameraTargetID, configID, trace, frame, hasImage);
--CREATE INDEX idx_FrameInfo_configID_hasImage ON FrameInfo(configID, hasImage);
--CREATE INDEX idx_FrameInfo_configID_trace_hasImage ON FrameInfo(configID, trace, hasImage);
--CREATE INDEX idx_FrameInfo_configID_trace_frame_hasImage ON FrameInfo(configID, trace, frame, hasImage);
