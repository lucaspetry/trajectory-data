-- Foursquare NYC
CREATE TABLE info (
    field VARCHAR(500) PRIMARY KEY,
    value VARCHAR(1000)
);

INSERT INTO info (field, value) VALUES ('database-name', 'Foursquare NYC');
INSERT INTO info (field, value) VALUES ('database-type', 'Check-in');
INSERT INTO info (field, value) VALUES ('short-description', 'Foursquare is a local search-and-discovery service mobile app which provides search results for its users.');
INSERT INTO info (field, value) VALUES ('when', 'Apr. 12, 2012 - Feb. 26, 2013');
INSERT INTO info (field, value) VALUES ('where', 'New York City');
INSERT INTO info (field, value) VALUES ('source', 'Dingqi Yang, Daqing Zhang, Vincent W. Zheng, Zhiyong Yu. Modeling User Activity Preference by Leveraging User Spatial Temporal Characteristics in LBSNs. IEEE Trans. on Systems, Man, and Cybernetics: Systems, (TSMC), 45(1), 129-142, 2015.');
INSERT INTO info (field, value) VALUES ('url', 'https://sites.google.com/site/yangdingqi/home/foursquare-dataset');
INSERT INTO info (field, value) VALUES ('add-on-venue-description', 'Venue information collected from the Foursquare API.');
INSERT INTO info (field, value) VALUES ('add-on-venue-url', 'https://developer.foursquare.com/');
INSERT INTO info (field, value) VALUES ('add-on-weather-description', 'Weather information collected from the Weather Wunderground API.');
INSERT INTO info (field, value) VALUES ('add-on-weather-url', 'https://www.wunderground.com/weather/api/');


-- Foursquare Global
CREATE TABLE info (
    field VARCHAR(500) PRIMARY KEY,
    value VARCHAR(1000)
);

INSERT INTO info (field, value) VALUES ('database-name', 'Foursquare Global');
INSERT INTO info (field, value) VALUES ('database-type', 'Check-in');
INSERT INTO info (field, value) VALUES ('short-description', 'Foursquare is a local search-and-discovery service mobile app which provides search results for its users.');
INSERT INTO info (field, value) VALUES ('when', 'Apr. 2012 - Sep. 2013');
INSERT INTO info (field, value) VALUES ('where', 'World');
INSERT INTO info (field, value) VALUES ('source', '[1] Dingqi Yang, Daqing Zhang, Bingqing Qu. Participatory Cultural Mapping Based on Collective Behavior Data in Location Based Social Networks. ACM Trans. on Intelligent Systems and Technology (TIST), 2015. [2] Dingqi Yang, Daqing Zhang, Longbiao Chen, Bingqing Qu. NationTelescope: Monitoring and Visualizing Large-Scale Collective Behavior in LBSNs. Journal of Network and Computer Applications (JNCA), 55:170-180, 2015.');
INSERT INTO info (field, value) VALUES ('url', 'https://sites.google.com/site/yangdingqi/home/foursquare-dataset');
INSERT INTO info (field, value) VALUES ('add-on-venue-description', 'Venue information collected from the Foursquare API.');
INSERT INTO info (field, value) VALUES ('add-on-venue-url', 'https://developer.foursquare.com/');


-- Gowalla
CREATE TABLE info (
    field VARCHAR(500) PRIMARY KEY,
    value VARCHAR(1000)
);

INSERT INTO info (field, value) VALUES ('database-name', 'Gowalla');
INSERT INTO info (field, value) VALUES ('database-type', 'Check-in');
INSERT INTO info (field, value) VALUES ('short-description', 'Gowalla was once a location-based social networking website where users share their locations by checking-in');
INSERT INTO info (field, value) VALUES ('when', 'Feb. 2009 - Oct. 2010');
INSERT INTO info (field, value) VALUES ('where', 'World');
INSERT INTO info (field, value) VALUES ('source', '[1] E. Cho, S. A. Myers, J. Leskovec. Friendship and Mobility: Friendship and Mobility: User Movement in Location-Based Social Networks ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD), 2011.');
INSERT INTO info (field, value) VALUES ('url', 'https://snap.stanford.edu/data/loc-gowalla.html');


-- Brightkite
CREATE TABLE info (
    field VARCHAR(500) PRIMARY KEY,
    value VARCHAR(1000)
);

INSERT INTO info (field, value) VALUES ('database-name', 'Brighkite');
INSERT INTO info (field, value) VALUES ('database-type', 'Check-in');
INSERT INTO info (field, value) VALUES ('short-description', 'Brightkite was once a location-based social networking service provider where users shared their locations by checking-in.');
INSERT INTO info (field, value) VALUES ('when', 'Apr. 2008 - Oct. 2010');
INSERT INTO info (field, value) VALUES ('where', 'World');
INSERT INTO info (field, value) VALUES ('source', '[1] E. Cho, S. A. Myers, J. Leskovec. Friendship and Mobility: Friendship and Mobility: User Movement in Location-Based Social Networks ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD), 2011.');
INSERT INTO info (field, value) VALUES ('url', 'https://snap.stanford.edu/data/loc-brightkite.html');


-- Geolife
CREATE TABLE info (
    field VARCHAR(500) PRIMARY KEY,
    value VARCHAR(1000)
);

INSERT INTO info (field, value) VALUES ('database-name', 'Geolife');
INSERT INTO info (field, value) VALUES ('database-type', 'Raw Trajectory');
INSERT INTO info (field, value) VALUES ('short-description', 'This GPS trajectory dataset was collected in (Microsoft Research Asia) Geolife project by 182 users in a period of over three years.');
INSERT INTO info (field, value) VALUES ('when', 'Apr. 2007 - Aug. 2012');
INSERT INTO info (field, value) VALUES ('where', 'China');
INSERT INTO info (field, value) VALUES ('source', '[1] Yu Zheng, Lizhu Zhang, Xing Xie, Wei-Ying Ma. Mining interesting locations and travel sequences from GPS trajectories. In Proceedings of International conference on World Wild Web (WWW 2009), Madrid Spain. ACM Press: 791-800. [2] Yu Zheng, Quannan Li, Yukun Chen, Xing Xie, Wei-Ying Ma. Understanding Mobility Based on GPS Data. In Proceedings of ACM conference on Ubiquitous Computing (UbiComp 2008), Seoul, Korea. ACM Press: 312-321. [3] Yu Zheng, Xing Xie, Wei-Ying Ma, GeoLife: A Collaborative Social Networking Service among User, location and trajectory. Invited paper, in IEEE Data Engineering Bulletin. 33, 2, 2010, pp. 32-40.');
INSERT INTO info (field, value) VALUES ('url', 'https://www.microsoft.com/en-us/download/details.aspx?id=52367&from=https%3A%2F%2Fresearch.microsoft.com%2Fen-us%2Fdownloads%2Fb16d359d-d164-469e-9fd4-daa38f2b2e13%2F');


-- Taxicab
CREATE TABLE info (
    field VARCHAR(500) PRIMARY KEY,
    value VARCHAR(1000)
);

INSERT INTO info (field, value) VALUES ('database-name', 'CRAWDAD Taxicab');
INSERT INTO info (field, value) VALUES ('database-type', 'Raw Trajectory');
INSERT INTO info (field, value) VALUES ('short-description', 'Dataset of mobility traces of taxi cabs in San Francisco, USA.');
INSERT INTO info (field, value) VALUES ('when', 'May 2008');
INSERT INTO info (field, value) VALUES ('where', 'San Francisco, CA, USA');
INSERT INTO info (field, value) VALUES ('source', '[1] Piorkowski, Michal, Natasa Sarafijanovic-Djukic, and Matthias Grossglauser. "A parsimonious model of mobile partitioned networks with clustering." 2009 First International Communication Systems and Networks and Workshops. IEEE, 2009.');
INSERT INTO info (field, value) VALUES ('url', 'https://crawdad.org/epfl/mobility/20090224/');