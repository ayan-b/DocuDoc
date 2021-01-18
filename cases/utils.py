from social_django.models import UserSocialAuth

GROUP_TO_IDX = {
    1: 'patient',
    2: 'hospital',
    3: 'pharmacy',
    4: 'diagnosis_center',
}

TEXT_TO_ID = {
    'Onset Comments': 108165370,
    'Context Comments': 108165371,
    'Modifying Factors Comments': 108165372,
    'Quality Comments': 108165373,
    'Severity Comments': 108165374,
    'Duration Comments': 108165375,
    'Associated Symptoms Comments ': 108165376,
    'Previous Treatment': 108165378,
    'Location Comments': 108165379,
    'Date of last PE': 108165389,
    'Past Medical History Freewrite': 108165390,
    'Comments': 108165641,
    'Occupation': 108165394,
    'PCP': 108165408,
    'Other substances': 108165415,
    "Patient's diet": 108165416,
    'PCP Contact Information': 108165417,
    'Potential Environmental Pathogen': 108165422, 'Endo Comments': 108165425, 'General Comments': 108165475,
    'Skin Comments': 108165481, 'HEENT Comments': 108165478, 'Neck Comments': 108165485,
    'Breasts Comments': 108165499, 'CV Comments': 108165444, 'Resp Comments': 108165447, 'GI Comments': 108165450,
    'Urinary Comments': 108165553, 'Genital (Male) Comments': 108165456, 'Periph. Vasc. Comments': 108165461,
    'MSK Comments': 108165545, 'Neuro Comments': 108165502, 'Genital (Female) Comments': 108165471,
    'Psychiatric Comments': 108165472, 'Cardiovascular Comments': 108165487, 'Lungs Comments': 108165490,
    'Abdomen Comments': 108165493, 'MSK Comments ': 108165496, 'Extrem Comments': 108165505, 'Assessment': 108165506,
    'Referrals ': 108165718
    , 'Lab Comments': 108165515, 'Radiology Comments': 108165516, 'PT Recommendation Comments': 108165517,
    'Home health comments': 108165518, 'Referral Comments': 108165731, 'Education Comments': 108165729,
    'Diet Comments': 108165521, 'General Instruction Comments': 108165522, 'Chief Complaint': 108165523,
    'Add. Complaint': 108165525, 'HPI': 108165526, 'Quality, Duration, Frequency': 108165527, 'Severity': 108165528,
    'Past/Current TX': 108165529, 'Family HX': 108165530, 'Past Medical HX': 108165531, 'Temp Comments': 108165533,
    'Perspiration Comments': 108165535, 'Skin/Hair Comments': 108165537, 'HA/Dizziness Comments': 108165539,
    'EENT/Phlegm Comments': 108165541, 'Chest, CV, RESP Comments': 108165543, 'Appetite/Thirst Comments': 108165547,
    'Digestion Comments': 108165549, 'Stool Comments': 108165551, 'Reproductive (Female) Comments': 108165555,
    'Reproductive (Male) Comments': 108165557, 'Sleep Comments': 108165560, 'Diet': 108165716, 'Activities': 108165563,
    'Onset': 108165566, 'Palliative/Provocative': 108165567, 'Region/Radiation': 108165568, 'Timing': 108165569,
    'TX Concerns/Expectations': 108165570, 'Social HX': 108165571, 'Energy Comments': 108165590,
    'Mental Emotional Comments': 108165592, 'Exercise': 108165730, 'Associated Symptoms': 108165594,
    "Patient's Explanation of Cause": 108165595, 'Chief Complaint Other': 108165598,
    'Medical Conditions Other': 108165636, 'Assessment Dialogue': 108165673, 'PLAN: Other Specific Orders': 108165677,
    'Syndrome Diagnosis CC': 108165690, 'TCM Pattern Differentiation CC': 108165691,
    'Signs: Pattern Confirmation C2': 108165693, 'Prognosis Comments CC': 108165694,
    'Signs: Pattern ConfirmationCC': 108165695, 'Additional Patterns': 108165696,
    'Syndrome Diagnosis complaint 2': 108165697, 'TCM Pattern Differentiation C2': 108165698,
    'Prognosis Comments C2': 108165700, 'Additional Signs': 108165701, 'TREATMENT PRINCIPLES': 108165702,
    'Appropriate Tx Modalities': 108165703, 'Acu Tx (1)': 108165707, 'Acu Tx (2)': 108165708,
    'Herbal Formula (1)': 108165710, 'Herb Dosage (1)': 108165711,
    'Herbal Formula (2)': 108165712,
    'Herb Dosage (2)': 108165713,
    'Add. Recommendations': 108165717,
    'Moxa Tx (1)': 108165721,
    'Moxa Tx (2)': 108165722,
    'Add. Modalities Comments (1)': 108165723,
    'Herb Comments (1)': 108165725,
    'Herb Comments (2)': 108165727,
    'Add. Mods. Comments (2):': 108165733,
    'Who referred you? ': 108165736,
    'Anything special we need to know': 108165739}


def get_group(user):
    for idx, group in GROUP_TO_IDX.items():
        if user.groups.filter(name=group).exists():
            return idx
    return None


def get_token():
    """
    Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
    already signed in.
    """
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']
    return access_token


def get_clinical_note_field(clinical_note_field_text):
    return TEXT_TO_ID[clinical_note_field_text]
