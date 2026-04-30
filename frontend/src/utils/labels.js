export const CONTRACT_TYPE_LABELS = {
  employment_nda: 'Employment NDA',
  saas_service_agreement: 'SaaS Service Agreement',
  consulting_service_agreement: 'Consulting Services Agreement',
  software_license_agreement: 'Software License Agreement',
  data_processing_agreement: 'Data Processing Agreement',
  vendor_agreement: 'Vendor Agreement',
  partnership_agreement: 'Partnership Agreement',
  freelancer_agreement: 'Freelance / Independent Contractor Agreement',
  master_service_agreement: 'Master Service Agreement (MSA)',
  joint_venture_agreement: 'Joint Venture Agreement',
};

export const CONTRACT_TYPE_OPTIONS = Object.entries(CONTRACT_TYPE_LABELS).map(
  ([value, label]) => ({ value, label })
);

export const STATUS_LABELS = {
  draft: 'Draft',
  in_review: 'In Review',
  approved: 'Approved',
  signed: 'Signed',
  active: 'Active',
  terminated: 'Terminated',
};

export const STATUS_OPTIONS = Object.entries(STATUS_LABELS).map(
  ([value, label]) => ({ value, label })
);

export const JURISDICTION_OPTIONS = [
  { value: 'India', label: 'India' },
  { value: 'USA', label: 'United States' },
  { value: 'UK', label: 'United Kingdom' },
];

export const VARIANT_OPTIONS = [
  { value: 'Standard', label: 'Standard' },
  { value: 'Moderate', label: 'Moderate' },
  { value: 'Strict', label: 'Strict' },
];

export const PARTY_ROLE_LABELS = {
  party_a: 'Party A',
  party_b: 'Party B',
  party_c: 'Party C',
  witness_1: 'Witness 1',
  witness_2: 'Witness 2',
};

export const PARTY_ROLE_OPTIONS = Object.entries(PARTY_ROLE_LABELS).map(
  ([value, label]) => ({ value, label })
);

export const LEGAL_ENTITY_OPTIONS = [
  { value: 'company', label: 'Company' },
  { value: 'llp', label: 'LLP' },
  { value: 'individual', label: 'Individual' },
  { value: 'partnership', label: 'Partnership' },
];
