#!/usr/bin/env python
"""
Reproducible pilot draw from the Solis-Lemus et al. 2026 four-chamber heart cohort.

Source: Zenodo concept DOI 10.5281/zenodo.17048090, version 10.5281/zenodo.19351401
(2026-03-31, CC-BY 4.0). Groups, sex and paper case labels come from the record's
dataset_info.csv (columns Case, Status, Sex, Translation_case); zip sizes and md5
checksums from the Zenodo file list. Status C = control, WQRS = heart failure with
wide QRS, NQRS = heart failure with narrow QRS.

Draw: sort the IDs within each group, then draw one heart per group in the order
control, HF wide QRS, HF narrow QRS with numpy.random.default_rng(20261002).
Nothing is downloaded.
"""

import numpy as np

SEED = 20261002
ORDER = ['control', 'HF wide QRS', 'HF narrow QRS']

# (zip ID, group, sex, case label in paper, zip size [bytes], md5)
COHORT = [
    ('3L9ZV4XS', 'control', 'F', 'FC6', 787127741, '2a393f70dc56c4ce9a54178959f88a07'),
    ('591DW86I', 'HF wide QRS', 'F', 'FHF11', 1073122235, '7b1727836c27fb1db6514b244e4f069c'),
    ('5IM7QJF4', 'control', 'F', 'FC2', 306432207, '269c2564209df6c62bb701448aad1507'),
    ('627ZFI97', 'HF narrow QRS', 'F', 'FHF1', 707415698, 'b5570ece50938d9b0a3badfa9e206544'),
    ('66AL590N', 'control', 'M', 'MC10', 345566673, '9897e5770e7a421a28433f7afe25d6cf'),
    ('6G8DD8S5', 'HF wide QRS', 'F', 'FHF8', 382433273, '8e8122eb09e0b1b0a65d13303159576b'),
    ('7D98EVAR', 'HF narrow QRS', 'F', 'FHF6', 328210243, '48b4cc87b766d3fe6a70e481deb22f8a'),
    ('98EK6960', 'control', 'F', 'FC5', 307108150, 'e505ed46503d417588066938da804fa5'),
    ('98G5I5CE', 'HF narrow QRS', 'F', 'FHF7', 420350166, '993abb4a819d1aeec110099ede952825'),
    ('9HE9S8YK', 'control', 'M', 'MC6', 959461118, '3aff88908cf5ef8c168e04ea0dd3fc8d'),
    ('A1VMI1BL', 'control', 'M', 'MC3', 339970763, 'c89595781eff8b5d435496dfa0aae850'),
    ('A8NCPLRI', 'HF narrow QRS', 'M', 'MHF3', 640160129, '4148717a5f2b4246953f26d4fa5a74fc'),
    ('B782Q8ID', 'control', 'M', 'MC12', 440821850, 'bd5ab29fc826fcb486d344a49c76f932'),
    ('BJRXL8KY', 'HF narrow QRS', 'F', 'FHF3', 365771944, '60cc6c8ab7fe19fc97aaa5e88765b535'),
    ('BRUN0G9V', 'control', 'M', 'MC7', 285972612, '86e333295cce1f5e2f6fb2c930f6929b'),
    ('C21IDK9N', 'control', 'M', 'MC11', 343372853, 'fc446b704475380ba6843ab540a5495a'),
    ('CTW6MAJL', 'HF narrow QRS', 'F', 'FHF2', 252624665, '8e9e937cfd2059ddfd482f7d0c6e64e1'),
    ('D16RF7C3', 'control', 'F', 'FC7', 664787541, '2f1db5581e22edf8fbf54b04903fdee8'),
    ('DA8Q81SZ', 'control', 'M', 'MC4', 399416170, '6897a8245850f215d6e7984b3624237d'),
    ('DHIPF4L7', 'control', 'M', 'MC13', 298333712, 'a6e2181a1789b43ebde0f5c4798a4819'),
    ('DN98C3EZ', 'HF wide QRS', 'F', 'FHF12', 279978763, '63d9b3203d0f1b74b4629c73900ab78b'),
    ('FC14', 'control', 'F', 'Fc14', 424519081, '9d0a569246fac20b8573110c2f6a495e'),
    ('FC15', 'control', 'F', 'FC15', 304890157, '9d125d27072989dc96d9b6bc036baabf'),
    ('FC5', 'control', 'F', 'FC5', 268582876, '3d9472d78f0adf28cb37c6985b91f3e1'),
    ('FC7', 'control', 'F', 'FC7', 290447796, '885a3a069f42949c28ce35aba79380b7'),
    ('FM7ID9EE', 'control', 'M', 'MC1', 332316526, 'bfbd44e7b149b9bc123c24d06f1b77ae'),
    ('FQB3LGOY', 'HF wide QRS', 'F', 'FHF9', 320548689, 'fd8aac8cb8980f19c0d53ea89978a339'),
    ('H2JQVUUF', 'control', 'F', 'FC9', 254956629, '485824fe19e9090604f3da41fb57caf5'),
    ('LENYCA0B', 'HF narrow QRS', 'F', 'FHF5', 1292396133, '2e586f649f15f50a9196c79da318d147'),
    ('LLWYK03H', 'control', 'F', 'FC3', 274072792, 'f9dfba4fa08f1580bc1d1b23b7f76b83'),
    ('MHFw14', 'HF wide QRS', 'M', 'MHFw14', 461788251, '7c214834bb3b61a8546b285682d8f171'),
    ('MHFw16', 'HF wide QRS', 'M', 'MHFw16', 369934475, 'aff51daa5cc5f7a65b0bacf1ca11c0b2'),
    ('MHFw6', 'HF wide QRS', 'M', 'MHFw6', 482458356, '1be3b8d3d0d800029f2e7d05bfd11845'),
    ('MHFw8', 'HF wide QRS', 'M', 'MHFw8', 443103340, '429580caef4ed96a4fb517360f72a4a6'),
    ('MQWINMXL', 'control', 'M', 'MC2', 472439433, '4226c339d68879e5c4d2adabbdcbc450'),
    ('OA15VRI2', 'control', 'F', 'FC4', 302712753, 'f61aba997706ae058a38b9082b06298b'),
    ('PGXLUL41', 'HF narrow QRS', 'M', 'MHF2', 467677818, 'ca7e676b67b76ee355b47ec55f51bc86'),
    ('PJR4AHZO', 'HF wide QRS', 'F', 'FHF10', 326408641, '2971e1a4f4f46fba5481d5907bb2ba02'),
    ('QSBZPFZI', 'control', 'F', 'FC10', 282793608, 'fabd8dbf7b752fbeadf6dee64d3e32fe'),
    ('SKSXRBWF', 'control', 'F', 'FC8', 795228732, 'a3ee360612b83bd167b3eb94627810c4'),
    ('TCNI6BDU', 'HF wide QRS', 'F', 'FHF13', 335587691, '0c6c9f98498aad0977e8eb8dd11de520'),
    ('TNJAF3TK', 'HF wide QRS', 'M', 'MHF5', 424384856, 'f19b83b646eb2743295cc141eafc8277'),
    ('XBTL2UYF', 'control', 'M', 'MC8', 375019593, '15c4d6d28643a2176c8032b6bf17feb3'),
    ('XWSQF3JX', 'control', 'M', 'MC9', 352749511, '156898ad0eebeab1dd9099e916246578'),
    ('Y5HYEDL4', 'control', 'M', 'MC5', 358810389, 'a7e648775f75badcbfddb73df3e1d720'),
    ('YCBD3S9F', 'HF narrow QRS', 'M', 'MHF4', 605730015, '09dd843b1a11fe98563328f04c62dd1d'),
    ('Z8FT2XBQ', 'HF narrow QRS', 'M', 'MHF1', 401046765, 'e524e169be6bac634af7d3237a28c3c4'),
    ('MHFn31', 'HF narrow QRS', 'M', 'MHFn31', 404207288, '145f3642129018e9d29841d64632565e'),
    ('FFI8S7CY', 'HF wide QRS', 'M', 'MHF6', 322604903, 'ba636e2f1bd1eaa9902718ea0350c9f1'),
    ('N4TRHUUP', 'HF narrow QRS', 'M', 'MHF7', 1096072855, '29b034df85f341e1405a3e089f12e31b'),
]


def main():
    assert len(COHORT) == 50
    rng = np.random.default_rng(SEED)
    picks = []
    for group in ORDER:
        members = sorted(h for h in COHORT if h[1] == group)
        picks.append(members[rng.choice(len(members))])
    total = 0
    for h in picks:
        total += h[4]
        print(f'{h[0]:10s} {h[1]:14s} sex {h[2]}  case {h[3]:7s} {h[4] / 1e9:.2f} GB  md5 {h[5]}')
    print(f'total {total / 1e9:.2f} GB zipped')


if __name__ == '__main__':
    main()
