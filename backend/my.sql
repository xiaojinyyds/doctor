create table if not exists tenants
(
    id                        varchar(36)                                                                          not null comment '租户ID'
        primary key,
    name                      varchar(100)                                                                         not null comment '机构名称',
    short_name                varchar(50)                                                                          null comment '机构简称',
    type                      enum ('hospital', 'clinic', 'checkup_center', 'insurance') default 'hospital'        not null comment '机构类型',
    level                     varchar(20)                                                                          null comment '医院等级: 三甲/二甲/一甲',
    contact_person            varchar(50)                                                                          null comment '联系人',
    contact_phone             varchar(20)                                                                          null comment '联系电话',
    contact_email             varchar(100)                                                                         null comment '联系邮箱',
    address                   varchar(255)                                                                         null comment '机构地址',
    province                  varchar(50)                                                                          null comment '省份',
    city                      varchar(50)                                                                          null comment '城市',
    license_key               varchar(100)                                                                         null comment '授权码',
    status                    enum ('active', 'suspended', 'expired')                    default 'active'          not null comment '状态',
    expire_date               date                                                                                 null comment '到期日期',
    max_users                 int                                                        default 100               not null comment '最大用户数',
    max_assessments_per_month int                                                        default 1000              not null comment '每月最大筛查数',
    current_month_assessments int                                                        default 0                 not null comment '本月已使用筛查数',
    logo_url                  varchar(255)                                                                         null comment '机构Logo',
    settings                  json                                                                                 null comment '机构配置(报告模板、品牌色等)',
    created_at                timestamp                                                  default CURRENT_TIMESTAMP not null comment '创建时间',
    updated_at                timestamp                                                  default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint license_key
        unique (license_key)
)
    comment '租户表' collate = utf8mb4_unicode_ci;

create table if not exists tenant_statistics
(
    id                   varchar(36)                         not null comment '统计ID'
        primary key,
    tenant_id            varchar(36)                         not null comment '租户ID',
    stat_date            date                                not null comment '统计日期',
    total_users          int       default 0                 not null comment '总用户数',
    active_users         int       default 0                 not null comment '活跃用户数',
    total_assessments    int       default 0                 not null comment '总评估数',
    high_risk_count      int       default 0                 not null comment '高风险数量',
    medium_risk_count    int       default 0                 not null comment '中风险数量',
    low_risk_count       int       default 0                 not null comment '低风险数量',
    pending_review_count int       default 0                 not null comment '待审核数量',
    created_at           timestamp default CURRENT_TIMESTAMP not null comment '创建时间',
    updated_at           timestamp default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint uk_tenant_date
        unique (tenant_id, stat_date),
    constraint fk_statistics_tenant
        foreign key (tenant_id) references tenants (id)
            on update cascade on delete cascade
)
    comment '机构统计表' collate = utf8mb4_unicode_ci;

create index idx_stat_date
    on tenant_statistics (stat_date);

create index idx_tenant_id
    on tenant_statistics (tenant_id);

create index idx_expire_date
    on tenants (expire_date);

create index idx_status
    on tenants (status);

create index idx_type
    on tenants (type);

create table if not exists users
(
    id            varchar(36)                                                not null comment '用户ID'
        primary key,
    tenant_id     varchar(36)                                                null comment '所属租户ID',
    email         varchar(100)                                               not null comment '邮箱',
    phone         varchar(11)                                                null comment '手机号',
    password_hash varchar(255)                                               not null comment '密码哈希',
    nickname      varchar(50)                                                null comment '昵称',
    avatar_url    varchar(255)                                               null comment '头像URL',
    role          enum ('user', 'doctor', 'admin') default 'user'            null comment '角色',
    department    varchar(50)                                                null comment '科室',
    title         varchar(50)                                                null comment '职称',
    employee_id   varchar(50)                                                null comment '工号',
    status        enum ('active', 'disabled')      default 'active'          null comment '状态',
    is_active     tinyint(1)                       default 1                 not null comment '是否激活',
    created_at    timestamp                        default CURRENT_TIMESTAMP null comment '创建时间',
    updated_at    timestamp                        default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    last_login_at timestamp                                                  null comment '最后登录时间',
    constraint email
        unique (email),
    constraint phone
        unique (phone),
    constraint fk_users_tenant
        foreign key (tenant_id) references tenants (id)
            on update cascade
)
    comment '用户表' collate = utf8mb4_unicode_ci;

create table if not exists batch_screening_tasks
(
    id               varchar(36)                                                                                  not null comment '任务ID'
        primary key,
    tenant_id        varchar(36)                                                                                  not null comment '租户ID',
    created_by       varchar(36)                                                                                  not null comment '创建人ID',
    task_name        varchar(100)                                                                                 null comment '任务名称',
    file_url         varchar(500)                                                                                 null comment '上传的Excel文件路径',
    file_name        varchar(255)                                                                                 null comment '原始文件名',
    total_count      int                                                                default 0                 not null comment '总数',
    success_count    int                                                                default 0                 not null comment '成功数',
    failed_count     int                                                                default 0                 not null comment '失败数',
    processing_count int                                                                default 0                 not null comment '处理中数量',
    status           enum ('pending', 'processing', 'completed', 'failed', 'cancelled') default 'pending'         not null comment '任务状态',
    progress         decimal(5, 2)                                                      default 0.00              not null comment '进度百分比',
    error_log        text                                                                                         null comment '错误日志',
    result_file_url  varchar(500)                                                                                 null comment '结果文件URL',
    started_at       timestamp                                                                                    null comment '开始时间',
    completed_at     timestamp                                                                                    null comment '完成时间',
    created_at       timestamp                                                          default CURRENT_TIMESTAMP not null comment '创建时间',
    updated_at       timestamp                                                          default CURRENT_TIMESTAMP not null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint fk_batch_tasks_creator
        foreign key (created_by) references users (id)
            on update cascade,
    constraint fk_batch_tasks_tenant
        foreign key (tenant_id) references tenants (id)
            on update cascade
)
    comment '批量筛查任务表' collate = utf8mb4_unicode_ci;

create index idx_created_at
    on batch_screening_tasks (created_at);

create index idx_created_by
    on batch_screening_tasks (created_by);

create index idx_status
    on batch_screening_tasks (status);

create index idx_tenant_id
    on batch_screening_tasks (tenant_id);

create table if not exists medical_images
(
    id                varchar(36)                                                                      not null comment '影像ID'
        primary key,
    tenant_id         varchar(36)                                                                      null comment '所属租户ID',
    user_id           varchar(36)                                                                      not null comment '用户ID',
    original_filename varchar(255)                                                                     not null comment '原始文件名',
    file_url          varchar(500)                                                                     not null comment '文件存储URL',
    file_size         int                                                                              not null comment '文件大小(字节)',
    file_format       varchar(20)                                                                      not null comment '文件格式(png/jpg/jpeg/dicom)',
    image_type        varchar(50)                                          default 'breast_ultrasound' null comment '影像类型(breast_ultrasound/ct/mri/xray)',
    body_part         varchar(50)                                          default 'breast'            null comment '检查部位',
    image_width       int                                                                              null comment '图像宽度',
    image_height      int                                                                              null comment '图像高度',
    acquisition_date  date                                                                             null comment '影像采集日期',
    institution       varchar(200)                                                                     null comment '检查机构',
    upload_status     enum ('pending', 'uploaded', 'failed')               default 'uploaded'          null comment '上传状态',
    analysis_status   enum ('pending', 'analyzing', 'completed', 'failed') default 'pending'           null comment '分析状态',
    created_at        timestamp                                            default CURRENT_TIMESTAMP   null comment '上传时间',
    updated_at        timestamp                                            default CURRENT_TIMESTAMP   null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint fk_medical_images_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    comment '医学影像上传记录表' collate = utf8mb4_unicode_ci;

create table if not exists image_analysis_results
(
    id                 varchar(36)                            not null comment '分析结果ID'
        primary key,
    tenant_id          varchar(36)                            null comment '所属租户ID',
    image_id           varchar(36)                            not null comment '影像ID',
    user_id            varchar(36)                            not null comment '用户ID',
    predicted_class    varchar(50)                            not null comment '预测类别(normal/benign/malignant)',
    predicted_class_cn varchar(50)                            not null comment '预测类别中文(正常/良性肿瘤/恶性肿瘤)',
    confidence         decimal(5, 4)                          not null comment '置信度(0-1)',
    prob_normal        decimal(5, 4)                          null comment '正常概率',
    prob_benign        decimal(5, 4)                          null comment '良性概率',
    prob_malignant     decimal(5, 4)                          null comment '恶性概率',
    risk_level         varchar(20)                            not null comment '风险等级(低风险/中风险/高风险)',
    risk_score         decimal(5, 4)                          null comment '风险分数',
    ai_recommendation  text                                   not null comment 'AI生成的医疗建议',
    heatmap_url        varchar(500)                           null comment '热力图URL(Grad-CAM)',
    attention_map_url  varchar(500)                           null comment '注意力图URL',
    model_name         varchar(100) default 'ResNet18'        null comment '使用的模型名称',
    model_version      varchar(50)  default 'v1.0'            null comment '模型版本',
    inference_time_ms  int                                    null comment '推理时间(毫秒)',
    reviewed_by_doctor tinyint(1)   default 0                 null comment '是否经医生审核',
    doctor_id          varchar(36)                            null comment '审核医生ID',
    doctor_opinion     text                                   null comment '医生意见',
    reviewed_at        timestamp                              null comment '审核时间',
    created_at         timestamp    default CURRENT_TIMESTAMP null comment '分析时间',
    updated_at         timestamp    default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint fk_image_results_doctor
        foreign key (doctor_id) references users (id)
            on delete set null,
    constraint fk_image_results_image
        foreign key (image_id) references medical_images (id)
            on delete cascade,
    constraint fk_image_results_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    comment '医学影像识别结果表' collate = utf8mb4_unicode_ci;

create table if not exists image_analysis_history
(
    id                 varchar(36)                           not null comment '历史记录ID'
        primary key,
    image_id           varchar(36)                           not null comment '影像ID',
    analysis_result_id varchar(36)                           not null comment '分析结果ID',
    user_id            varchar(36)                           not null comment '用户ID',
    analysis_type      varchar(50) default 'classification'  null comment '分析类型(classification/segmentation/detection)',
    parameters         json                                  null comment '分析参数',
    result_snapshot    json                                  not null comment '结果快照(完整JSON)',
    compared_with      varchar(36)                           null comment '对比的影像ID',
    comparison_notes   text                                  null comment '对比说明',
    created_at         timestamp   default CURRENT_TIMESTAMP null comment '分析时间',
    constraint fk_history_image
        foreign key (image_id) references medical_images (id)
            on delete cascade,
    constraint fk_history_result
        foreign key (analysis_result_id) references image_analysis_results (id)
            on delete cascade,
    constraint fk_history_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    comment '影像分析历史记录表' collate = utf8mb4_unicode_ci;

create index idx_analysis_type
    on image_analysis_history (analysis_type);

create index idx_created_at
    on image_analysis_history (created_at);

create index idx_image_id
    on image_analysis_history (image_id);

create index idx_user_id
    on image_analysis_history (user_id);

create index idx_created_at
    on image_analysis_results (created_at);

create index idx_image_id
    on image_analysis_results (image_id);

create index idx_predicted_class
    on image_analysis_results (predicted_class);

create index idx_reviewed
    on image_analysis_results (reviewed_by_doctor);

create index idx_risk_level
    on image_analysis_results (risk_level);

create index idx_tenant_id
    on image_analysis_results (tenant_id);

create index idx_user_id
    on image_analysis_results (user_id);

create table if not exists image_annotations
(
    id                 varchar(36)                                                          not null comment '标注ID'
        primary key,
    image_id           varchar(36)                                                          not null comment '影像ID',
    annotator_id       varchar(36)                                                          not null comment '标注人ID（医生）',
    true_label         varchar(50)                                                          not null comment '真实标签(normal/benign/malignant)',
    true_label_cn      varchar(50)                                                          not null comment '真实标签中文',
    lesion_count       int                                        default 0                 null comment '病灶数量',
    lesion_locations   json                                                                 null comment '病灶位置信息',
    lesion_sizes       json                                                                 null comment '病灶大小信息',
    pathology_result   varchar(100)                                                         null comment '病理结果',
    clinical_diagnosis text                                                                 null comment '临床诊断',
    additional_notes   text                                                                 null comment '补充说明',
    annotation_quality enum ('low', 'medium', 'high')             default 'medium'          null comment '标注质量',
    confidence_level   enum ('uncertain', 'probable', 'definite') default 'probable'        null comment '确信程度',
    ai_prediction      varchar(50)                                                          null comment 'AI预测结果',
    ai_correct         tinyint(1)                                                           null comment 'AI预测是否正确',
    created_at         timestamp                                  default CURRENT_TIMESTAMP null comment '标注时间',
    updated_at         timestamp                                  default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint fk_annotations_annotator
        foreign key (annotator_id) references users (id)
            on delete cascade,
    constraint fk_annotations_image
        foreign key (image_id) references medical_images (id)
            on delete cascade
)
    comment '医学影像标注表' collate = utf8mb4_unicode_ci;

create index idx_ai_correct
    on image_annotations (ai_correct);

create index idx_annotator_id
    on image_annotations (annotator_id);

create index idx_created_at
    on image_annotations (created_at);

create index idx_image_id
    on image_annotations (image_id);

create index idx_true_label
    on image_annotations (true_label);

create index idx_analysis_status
    on medical_images (analysis_status);

create index idx_created_at
    on medical_images (created_at);

create index idx_image_type
    on medical_images (image_type);

create index idx_tenant_id
    on medical_images (tenant_id);

create index idx_user_id
    on medical_images (user_id);

create table if not exists operation_logs
(
    id                varchar(36)                         not null comment '日志ID'
        primary key,
    tenant_id         varchar(36)                         null comment '租户ID',
    user_id           varchar(36)                         null comment '操作人ID',
    action            varchar(50)                         not null comment '操作类型',
    action_name       varchar(100)                        null comment '操作名称',
    resource_type     varchar(50)                         null comment '资源类型',
    resource_id       varchar(36)                         null comment '资源ID',
    details           json                                null comment '详细信息',
    ip_address        varchar(50)                         null comment 'IP地址',
    user_agent        text                                null comment '用户代理',
    request_method    varchar(10)                         null comment '请求方法',
    request_url       varchar(500)                        null comment '请求URL',
    response_status   int                                 null comment '响应状态码',
    execution_time_ms int                                 null comment '执行时间(毫秒)',
    created_at        timestamp default CURRENT_TIMESTAMP not null comment '操作时间',
    constraint fk_logs_tenant
        foreign key (tenant_id) references tenants (id)
            on update cascade on delete cascade,
    constraint fk_logs_user
        foreign key (user_id) references users (id)
            on update cascade on delete set null
)
    comment '操作日志表' collate = utf8mb4_unicode_ci;

create index idx_action
    on operation_logs (action);

create index idx_created_at
    on operation_logs (created_at);

create index idx_resource_type
    on operation_logs (resource_type);

create index idx_tenant_id
    on operation_logs (tenant_id);

create index idx_user_id
    on operation_logs (user_id);

create table if not exists questionnaires
(
    id                       varchar(36)                           not null comment '问卷ID'
        primary key,
    tenant_id                varchar(36)                           null comment '所属租户ID',
    user_id                  varchar(36)                           not null comment '用户ID',
    age                      int                                   not null comment '年龄',
    gender                   varchar(10)                           not null comment '性别',
    height                   decimal(5, 2)                         not null comment '身高(cm)',
    weight                   decimal(5, 2)                         not null comment '体重(kg)',
    bmi                      decimal(4, 2) as ((`weight` / pow((`height` / 100), 2))) stored comment 'BMI指数',
    smoking_history          json                                  null comment '吸烟史',
    alcohol_history          json                                  null comment '饮酒史',
    exercise_habit           varchar(50)                           null comment '运动习惯',
    diet_habits              json                                  null comment '饮食习惯',
    sleep_quality            varchar(50)                           null comment '睡眠质量',
    chronic_diseases         json                                  null comment '慢性病史',
    family_cancer_history    json                                  null comment '家族肿瘤史',
    surgery_history          json                                  null comment '手术史',
    medication_history       json                                  null comment '用药史',
    symptoms                 json                                  null comment '近期症状',
    recent_abnormalities     json                                  null comment '既往检查异常',
    last_checkup             varchar(50)                           null comment '上次体检时间',
    occupational_exposure    json                                  null comment '职业暴露(化学品/粉尘/辐射/生物因子等)',
    environmental_factors    json                                  null comment '环境因素(空气质量/污染暴露/居住环境等)',
    living_environment       varchar(50)                           null comment '居住环境类型(城市/农村/工业区等)',
    vegetable_fruit_intake   varchar(50)                           null comment '蔬菜水果摄入频率',
    red_meat_intake          varchar(50)                           null comment '红肉摄入频率',
    processed_food_intake    varchar(50)                           null comment '加工食品摄入频率',
    pickled_food_intake      varchar(50)                           null comment '腌制食品摄入频率',
    dairy_intake             varchar(50)                           null comment '乳制品摄入频率',
    menstrual_status         varchar(50)                           null comment '月经状况(正常/绝经/异常等)',
    pregnancy_history        json                                  null comment '妊娠史(次数/年龄/并发症等)',
    breastfeeding_history    json                                  null comment '哺乳史(时长/方式等)',
    hormone_therapy          json                                  null comment '激素治疗史(避孕药/激素替代疗法等)',
    stress_level             varchar(50)                           null comment '压力水平(低/中/高)',
    work_rest_pattern        varchar(50)                           null comment '作息规律性(规律/一般/不规律/熬夜)',
    mental_health            varchar(50)                           null comment '心理健康状况(良好/焦虑/抑郁等)',
    screening_history        json                                  null comment '筛查历史(肿瘤标志物/影像学检查/内镜检查等)',
    abnormal_results_history json                                  null comment '异常结果历史(具体异常项目及时间)',
    status                   varchar(20) default 'completed'       null comment '状态: draft/completed',
    created_at               timestamp   default CURRENT_TIMESTAMP null comment '创建时间',
    updated_at               timestamp   default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint fk_questionnaires_tenant
        foreign key (tenant_id) references tenants (id)
            on update cascade,
    constraint questionnaires_ibfk_1
        foreign key (user_id) references users (id)
            on delete cascade
)
    comment '问卷数据表' collate = utf8mb4_unicode_ci;

create table if not exists assessments
(
    id                 varchar(36)                                                                     not null comment '评估ID'
        primary key,
    tenant_id          varchar(36)                                                                     null comment '所属租户ID',
    user_id            varchar(36)                                                                     not null comment '用户ID',
    questionnaire_id   varchar(36)                                                                     not null comment '问卷ID',
    overall_risk_score decimal(5, 4)                                                                   not null comment '综合风险分数(0-1)',
    overall_risk_level varchar(20)                                                                     not null comment '风险等级: 低/中/高/极高',
    status             enum ('pending', 'approved', 'rejected', 'cancelled') default 'pending'         not null comment '审核状态',
    reviewed_by        varchar(36)                                                                     null comment '审核医生ID',
    reviewed_at        timestamp                                                                       null comment '审核时间',
    doctor_comment     text                                                                            null comment '医生意见',
    doctor_risk_level  varchar(20)                                                                     null comment '医生判断的风险等级',
    is_batch           tinyint(1)                                            default 0                 not null comment '是否批量筛查',
    batch_task_id      varchar(36)                                                                     null comment '批量任务ID',
    risk_percentile    int                                                                             null comment '风险百分位',
    category_risks     json                                                                            not null comment '各类肿瘤风险',
    key_factors        json                                                                            not null comment '关键风险因素',
    shap_values        json                                                                            null comment 'SHAP值详细数据',
    model_version      varchar(50)                                           default 'v1.0'            null comment '模型版本',
    inference_time_ms  int                                                                             null comment '推理时间(毫秒)',
    created_at         timestamp                                             default CURRENT_TIMESTAMP null comment '评估时间',
    ai_recommendation  text                                                                            null comment 'AI生成的个性化健康建议',
    constraint assessments_ibfk_1
        foreign key (user_id) references users (id)
            on delete cascade,
    constraint assessments_ibfk_2
        foreign key (questionnaire_id) references questionnaires (id)
            on delete cascade,
    constraint fk_assessments_batch_task
        foreign key (batch_task_id) references batch_screening_tasks (id)
            on update cascade on delete set null,
    constraint fk_assessments_reviewer
        foreign key (reviewed_by) references users (id)
            on update cascade on delete set null,
    constraint fk_assessments_tenant
        foreign key (tenant_id) references tenants (id)
            on update cascade
)
    comment '风险评估结果表' collate = utf8mb4_unicode_ci;

create index idx_batch_task_id
    on assessments (batch_task_id);

create index idx_created_at
    on assessments (created_at);

create index idx_questionnaire_id
    on assessments (questionnaire_id);

create index idx_reviewed_by
    on assessments (reviewed_by);

create index idx_risk_level
    on assessments (overall_risk_level);

create index idx_status
    on assessments (status);

create index idx_tenant_id
    on assessments (tenant_id);

create index idx_user_id
    on assessments (user_id);

create table if not exists batch_task_items
(
    id                 varchar(36)                                                                   not null comment '明细ID'
        primary key,
    task_id            varchar(36)                                                                   not null comment '任务ID',
    `row_number`       int                                                                           not null comment 'Excel行号',
    patient_name       varchar(50)                                                                   null comment '患者姓名',
    patient_phone      varchar(20)                                                                   null comment '患者手机号',
    patient_id_card    varchar(20)                                                                   null comment '身份证号',
    questionnaire_data json                                                                          null comment '问卷数据',
    questionnaire_id   varchar(36)                                                                   null comment '生成的问卷ID',
    assessment_id      varchar(36)                                                                   null comment '生成的评估ID',
    status             enum ('pending', 'processing', 'success', 'failed') default 'pending'         not null comment '状态',
    error_message      text                                                                          null comment '错误信息',
    processed_at       timestamp                                                                     null comment '处理时间',
    created_at         timestamp                                           default CURRENT_TIMESTAMP not null comment '创建时间',
    constraint fk_batch_items_assessment
        foreign key (assessment_id) references assessments (id)
            on update cascade on delete set null,
    constraint fk_batch_items_questionnaire
        foreign key (questionnaire_id) references questionnaires (id)
            on update cascade on delete set null,
    constraint fk_batch_items_task
        foreign key (task_id) references batch_screening_tasks (id)
            on update cascade on delete cascade
)
    comment '批量任务明细表' collate = utf8mb4_unicode_ci;

create index idx_assessment_id
    on batch_task_items (assessment_id);

create index idx_status
    on batch_task_items (status);

create index idx_task_id
    on batch_task_items (task_id);

create table if not exists followup_plans
(
    id                  varchar(36)                                                                    not null comment '计划ID'
        primary key,
    user_id             varchar(36)                                                                    not null comment '用户ID',
    assessment_id       varchar(36)                                                                    null comment '触发该计划的评估ID',
    risk_level          varchar(20)                                                                    not null comment '风险等级(低风险/中低风险/中高风险/高风险)',
    interval_days       int                                                                            not null comment '随访间隔天数',
    total_followups     int                                                  default 4                 null comment '计划随访总次数',
    completed_count     int                                                  default 0                 null comment '已完成次数',
    next_followup_date  timestamp                                                                      not null comment '下次随访日期',
    status              enum ('pending', 'active', 'completed', 'cancelled') default 'active'          null comment '计划状态',
    is_active           tinyint(1)                                           default 1                 null comment '是否激活',
    notify_email        tinyint(1)                                           default 1                 null comment '邮件提醒',
    notify_sms          tinyint(1)                                           default 0                 null comment '短信提醒',
    advance_notify_days int                                                  default 3                 null comment '提前几天提醒',
    created_at          timestamp                                            default CURRENT_TIMESTAMP null comment '创建时间',
    updated_at          timestamp                                            default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint fk_followup_plans_assessment
        foreign key (assessment_id) references assessments (id)
            on delete set null,
    constraint fk_followup_plans_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    comment '随访计划表' collate = utf8mb4_unicode_ci;

create index idx_is_active
    on followup_plans (is_active);

create index idx_next_followup_date
    on followup_plans (next_followup_date);

create index idx_status
    on followup_plans (status);

create index idx_user_id
    on followup_plans (user_id);

create table if not exists followup_records
(
    id                   varchar(36)                                                                    not null comment '记录ID'
        primary key,
    plan_id              varchar(36)                                                                    not null comment '计划ID',
    user_id              varchar(36)                                                                    not null comment '用户ID',
    assessment_id        varchar(36)                                                                    null comment '本次随访关联的评估ID',
    sequence             int                                                                            not null comment '第几次随访',
    scheduled_date       timestamp                                                                      not null comment '计划随访日期',
    completed_date       timestamp                                                                      null comment '实际完成日期',
    status               enum ('pending', 'notified', 'completed', 'overdue') default 'pending'         null comment '记录状态',
    health_metrics       json                                                                           null comment '健康指标数据',
    risk_score_before    decimal(5, 4)                                                                  null comment '随访前风险分数',
    risk_score_after     decimal(5, 4)                                                                  null comment '随访后风险分数',
    risk_change          decimal(5, 4)                                                                  null comment '风险变化值',
    notification_sent    tinyint(1)                                           default 0                 null comment '是否已发送提醒',
    notification_sent_at timestamp                                                                      null comment '提醒发送时间',
    notes                text                                                                           null comment '随访备注',
    created_at           timestamp                                            default CURRENT_TIMESTAMP null comment '创建时间',
    constraint fk_followup_records_assessment
        foreign key (assessment_id) references assessments (id)
            on delete set null,
    constraint fk_followup_records_plan
        foreign key (plan_id) references followup_plans (id)
            on delete cascade,
    constraint fk_followup_records_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    comment '随访记录表' collate = utf8mb4_unicode_ci;

create index idx_plan_id
    on followup_records (plan_id);

create index idx_scheduled_date
    on followup_records (scheduled_date);

create index idx_status
    on followup_records (status);

create index idx_user_id
    on followup_records (user_id);

create table if not exists health_metric_logs
(
    id            varchar(36)                         not null comment '日志ID'
        primary key,
    user_id       varchar(36)                         not null comment '用户ID',
    metric_type   varchar(50)                         not null comment '指标类型(weight/blood_pressure_systolic/blood_pressure_diastolic/symptom_severity等)',
    metric_value  decimal(10, 2)                      not null comment '指标值',
    metric_unit   varchar(20)                         null comment '单位(kg/mmHg等)',
    assessment_id varchar(36)                         null comment '关联的评估ID',
    recorded_at   timestamp default CURRENT_TIMESTAMP null comment '记录时间',
    constraint fk_health_logs_assessment
        foreign key (assessment_id) references assessments (id)
            on delete set null,
    constraint fk_health_logs_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    comment '健康指标日志表' collate = utf8mb4_unicode_ci;

create index idx_metric_type
    on health_metric_logs (metric_type);

create index idx_recorded_at
    on health_metric_logs (recorded_at);

create index idx_user_id
    on health_metric_logs (user_id);

create index idx_user_metric
    on health_metric_logs (user_id, metric_type);

create table if not exists health_records
(
    id                   varchar(36)                                                      not null comment '档案ID'
        primary key,
    user_id              varchar(36)                                                      not null comment '用户ID',
    questionnaire_id     varchar(36)                                                      null comment '问卷ID',
    assessment_id        varchar(36)                                                      null comment '评估ID',
    image_ids            json                                                             null comment '关联的影像ID列表',
    overall_health_score decimal(5, 4)                                                    null comment '综合健康分数',
    risk_summary         json                                                             null comment '风险汇总',
    follow_up_required   tinyint(1)                             default 0                 null comment '是否需要随访',
    follow_up_date       date                                                             null comment '建议随访日期',
    follow_up_items      json                                                             null comment '随访项目',
    status               enum ('active', 'archived', 'deleted') default 'active'          null comment '档案状态',
    created_at           timestamp                              default CURRENT_TIMESTAMP null comment '创建时间',
    updated_at           timestamp                              default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP comment '更新时间',
    constraint fk_records_assessment
        foreign key (assessment_id) references assessments (id)
            on delete set null,
    constraint fk_records_questionnaire
        foreign key (questionnaire_id) references questionnaires (id)
            on delete set null,
    constraint fk_records_user
        foreign key (user_id) references users (id)
            on delete cascade
)
    comment '综合健康档案表' collate = utf8mb4_unicode_ci;

create index idx_created_at
    on health_records (created_at);

create index idx_follow_up_date
    on health_records (follow_up_date);

create index idx_status
    on health_records (status);

create index idx_user_id
    on health_records (user_id);

create index idx_created_at
    on questionnaires (created_at);

create index idx_status
    on questionnaires (status);

create index idx_tenant_id
    on questionnaires (tenant_id);

create index idx_user_id
    on questionnaires (user_id);

create table if not exists recommendations
(
    id            varchar(36)                         not null comment '建议ID'
        primary key,
    tenant_id     varchar(36)                         null comment '所属租户ID',
    assessment_id varchar(36)                         not null comment '评估ID',
    category      varchar(50)                         not null comment '建议分类: lifestyle/diet/screening/medical',
    title         varchar(200)                        not null comment '建议标题',
    content       text                                not null comment '建议内容',
    priority      int       default 1                 null comment '优先级(0最高)',
    created_at    timestamp default CURRENT_TIMESTAMP null comment '创建时间',
    constraint recommendations_ibfk_1
        foreign key (assessment_id) references assessments (id)
            on delete cascade
)
    comment '健康建议表' collate = utf8mb4_unicode_ci;

create index idx_assessment_id
    on recommendations (assessment_id);

create index idx_category
    on recommendations (category);

create index idx_priority
    on recommendations (priority);

create index idx_tenant_id
    on recommendations (tenant_id);

create table if not exists reports
(
    id              varchar(36)                           not null comment '报告ID'
        primary key,
    tenant_id       varchar(36)                           null comment '所属租户ID',
    user_id         varchar(36)                           not null comment '用户ID',
    assessment_id   varchar(36)                           not null comment '评估ID',
    report_type     varchar(20) default 'web'             null comment '报告类型: web/pdf',
    pdf_url         varchar(255)                          null comment 'PDF文件URL',
    share_token     varchar(100)                          null comment '分享令牌',
    share_password  varchar(100)                          null comment '访问密码',
    share_expire_at timestamp                             null comment '分享过期时间',
    is_public       tinyint(1)  default 0                 not null comment '是否公开',
    view_count      int         default 0                 null comment '查看次数',
    access_count    int         default 0                 not null comment '访问次数',
    created_at      timestamp   default CURRENT_TIMESTAMP null comment '创建时间',
    constraint share_token
        unique (share_token),
    constraint reports_ibfk_1
        foreign key (user_id) references users (id)
            on delete cascade,
    constraint reports_ibfk_2
        foreign key (assessment_id) references assessments (id)
            on delete cascade
)
    comment '报告记录表' collate = utf8mb4_unicode_ci;

create index idx_assessment_id
    on reports (assessment_id);

create index idx_share_expire_at
    on reports (share_expire_at);

create index idx_share_token
    on reports (share_token);

create index idx_tenant_id
    on reports (tenant_id);

create index idx_user_id
    on reports (user_id);

create index idx_email
    on users (email);

create index idx_phone
    on users (phone);

create index idx_role
    on users (role);

create index idx_status
    on users (status);

create index idx_tenant_id
    on users (tenant_id);

