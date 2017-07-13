use image_labels;
-- use 'in' to capture 0s b/c '!="NULL"' ignores 0s
select * from classifications where label_id in (0,1,2,3); 
