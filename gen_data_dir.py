import json
from pathlib import Path
import os
from normilize import normilize_line
from collections import defaultdict

def aeneas_json2kaldi_data(aeneas_json_paths, audio_paths, out_data_dir, normilize=True, rewrite=False):
    """
    Generates a kaldi data dir from the aeneas json.
    :param aeneas_json_paths: list of paths to a aeneas jsons
    :param audio_paths: list of paths to the corresponding wav files
    :param out_data_dir: the output data dir
    :return:
    """

    # setting paths
    aeneas_json_paths = [Path(path) for path in aeneas_json_paths]
    audio_paths = [Path(path) for path in audio_paths]
    out_data_dir = Path(out_data_dir)

    if not rewrite:
        assert not out_data_dir.exists(), f'data dir in {out_data_dir} already exists!'

    utts = {}
    audios = {}
    for json_path, audio_path in zip(aeneas_json_paths,audio_paths):
        # parse json
        j = json.load(open(json_path, 'r', encoding='utf8'))

        # generate audi_id
        audio_id = audio_path.stem
        audios[audio_id] = audio_path

        # generate a dictionary of utterances by utt_id
        for f in j['fragments']:
            # generate utterance
            utt_start = float(f['begin'])
            utt_end = float(f['end'])
            utt_spk = audio_id
            utt_id = f'{audio_id}-{str(int(utt_start * 100)).zfill(7)}-{str(int(utt_end * 100)).zfill(7)}'
            if normilize:
                utt_text = normilize_line(f['lines'][0])
            else:
                utt_text = f['lines'][0]

            utts[utt_id] = {'id': utt_id,
                            'audio_id': audio_id,
                            'start': round(utt_start, 2),
                            'end': round(utt_end, 2),
                            'speaker': utt_spk,
                            'text': utt_text}

    # set filenames
    wav_scp = out_data_dir / 'wav.scp'
    utt2spk = out_data_dir / 'utt2spk'
    segments = out_data_dir / 'segments'
    text = out_data_dir / 'text'

    # make dir
    if not out_data_dir.exists():
        os.makedirs(str(out_data_dir))

    with open(wav_scp, 'w', encoding='utf-8') as wav_f:
        for audio_id in audios:
            wav_f.write(f'{audio_id} {audios[audio_id]}\n')

    with open(utt2spk, 'w', encoding='utf-8') as utt2spk_f, \
            open(segments, 'w', encoding='utf-8') as segments_f, \
            open(text, 'w', encoding='utf-8') as text_f:
        for utt_id in utts:
            utt2spk_f.write(f'{utt_id} {utts[utt_id]["speaker"]}\n')
            segments_f.write(f'{utt_id} {utts[utt_id]["audio_id"]} {utts[utt_id]["start"]} {utts[utt_id]["end"]}\n')
            text_f.write(f'{utt_id} {utts[utt_id]["text"]}\n')


def text_with_unk(text_path, lexicon_path, out_text_path):

    # setting paths
    text_path = Path(text_path)
    lexicon_path = Path(lexicon_path)
    out_text_path = Path(out_text_path)

    # read text
    text = [x.split() for x in open(text_path, 'r', encoding='utf-8').read().split('\n') if x]

    # read lexicon
    lexicon = defaultdict(list)
    [lexicon[x.split()[0]].append(x.split()[1:]) for x in open(lexicon_path, 'r', encoding='utf-8').read().split('\n') if x]

    with open(out_text_path, 'w', encoding='utf-8') as f:
        for line in text:
            f.write(f'{line[0]}')
            for word in line[1:]:
                f.write(f' {word}') if word in lexicon else f.write(f' <UNK>')
            f.write(f'\n')


def text2plane(texts_list, out_text_file):

    out_text_file = Path(out_text_file)

    with open(out_text_file, 'w', encoding='utf-8') as out_text:

        for text_file in texts_list:
            f = open(text_file, "r")
            lines = list(f)
            f.close()

            for line in lines:
                utt_text = normilize_line(line)
                out_text.write(f'{utt_text}\n')


if __name__ == '__main__':
    # aeneas_json2kaldi_data(['/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_1.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_2.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_3.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_4.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_5.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_6.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_7.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_8.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_9.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_10.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_11.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_12.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_13.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_14.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_15.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_16.json',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_17.json'
    #                         ],
    #                        ['/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_1.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_2.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_3.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_4.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_5.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_6.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_7.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_8.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_9.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_10.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_11.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_12.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_13.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_14.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_15.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_16.wav',
    #                         '/Users/mac/Datasets/ukrainian/panas_yasla/panas_yasla_17.wav'
    #                         ],
    #                        '/Users/mac/Datasets/ukrainian/panas_yasla/data',
    #                        rewrite=True)
    # text_with_unk('/Users/mac/Datasets/ukrainian/zapovit/data/text_original',
    #               '/Users/mac/Datasets/ukrainian/lang/lexicon.txt',
    #               '/Users/mac/Datasets/ukrainian/zapovit/data/text')

#     text2plane(['/Users/mac/Datasets/ukrainian/texts/Administrativne_pravo._Zagalna_chastina_1374748722.txt',
# '/Users/mac/Datasets/ukrainian/texts/Aivengo_1411749087.txt',
# '/Users/mac/Datasets/ukrainian/texts/Akvariym_1425046581.txt',
# '/Users/mac/Datasets/ukrainian/texts/Albatrosi_1425046367.txt',
# '/Users/mac/Datasets/ukrainian/texts/Almazne_zhorno.txt',
# '/Users/mac/Datasets/ukrainian/texts/Amnistiya_dlya_Hakera_1446666984.txt',
# '/Users/mac/Datasets/ukrainian/texts/Anhely-po-desyat-shylinhiv-Peter-Adams.txt',
# '/Users/mac/Datasets/ukrainian/texts/Antonii_i_Kleopatra_1407169364.txt',
# '/Users/mac/Datasets/ukrainian/texts/Arahnofobiya_1412632437.txt',
# '/Users/mac/Datasets/ukrainian/texts/Arystokrat_iz_Vapniarky.txt',
# '/Users/mac/Datasets/ukrainian/texts/Aviron.txt',
# '/Users/mac/Datasets/ukrainian/texts/Babysi_takoj_byli_divchatami_1450631964.txt',
# '/Users/mac/Datasets/ukrainian/texts/Batalionneobmyndirovanih_1409154131.txt',
# '/Users/mac/Datasets/ukrainian/texts/Bitva_pid_Konotopom_1403771998.txt',
# '/Users/mac/Datasets/ukrainian/texts/BoginyaiKonsyltant_1413400353.txt',
# '/Users/mac/Datasets/ukrainian/texts/Bojii_svitilnik.Kylya_dlya_bosa_1370255033.txt',
# '/Users/mac/Datasets/ukrainian/texts/Bojki_1371652311.txt',
# '/Users/mac/Datasets/ukrainian/texts/Bortsi_za_pravdu.txt',
# '/Users/mac/Datasets/ukrainian/texts/Brati_gromy_1374761623.txt',
# '/Users/mac/Datasets/ukrainian/texts/Brati_vognu_1374761694.txt',
# '/Users/mac/Datasets/ukrainian/texts/Brodiaha.txt',
# '/Users/mac/Datasets/ukrainian/texts/Byriyan_1371653477.txt',
# '/Users/mac/Datasets/ukrainian/texts/Ctvorennya_VChK_-_interpretaciya_vidomoj_problemi_1378134741.txt',
# '/Users/mac/Datasets/ukrainian/texts/Detektyv_Bliumkvist_ryzykuie.txt',
# '/Users/mac/Datasets/ukrainian/texts/Detektyv_Bliumkvist_zdobuvaie_slavu.txt',
# '/Users/mac/Datasets/ukrainian/texts/Dolina_sovisti_1446666775.txt',
# '/Users/mac/Datasets/ukrainian/texts/Dovha_nich_nad_Sunzheiu.txt',
# '/Users/mac/Datasets/ukrainian/texts/Etud_y_yasno-chervonih_kolorah_1397486099.txt',
# '/Users/mac/Datasets/ukrainian/texts/Gra_Dzerkal__1371139671.txt',
# '/Users/mac/Datasets/ukrainian/texts/Hotuietsia_vbyvstvo.txt',
# '/Users/mac/Datasets/ukrainian/texts/HronikiYakybaVendrovicha_1413476031.txt',
# '/Users/mac/Datasets/ukrainian/texts/I_zhodnoi_versii.txt',
# '/Users/mac/Datasets/ukrainian/texts/Ilko_Lipei_-_karpatskii_rozbiinik_1375288375.txt',
# '/Users/mac/Datasets/ukrainian/texts/Inakodymstvo_na_Symshini._Zbirnik_dokymentiv_ta_materialiv_(1955-1990_roki)._Tom_1_1374835061.txt',
# '/Users/mac/Datasets/ukrainian/texts/Indiyanyn-Eduard-Klyajn.txt',
# '/Users/mac/Datasets/ukrainian/texts/Inspektor-i-nich-Brazilska-melodiya-Bohomyl-Rajnov.txt',
# '/Users/mac/Datasets/ukrainian/texts/Internacionalizm_chi_rysifikaciya_1369050586.txt',
# '/Users/mac/Datasets/ukrainian/texts/Istoriya-z-sobakamy-Avakum-Zahov--8-Andrej-Hulyashky.txt',
# '/Users/mac/Datasets/ukrainian/texts/Istoriya_radyanskoj_derjavi_1369146892.txt',
# '/Users/mac/Datasets/ukrainian/texts/Istoriyaykrajnskojliteratyrnojmovi_1428593985.txt',
# '/Users/mac/Datasets/ukrainian/texts/Ivan_Bogyn._Tom_1_1407860840.txt',
# '/Users/mac/Datasets/ukrainian/texts/Ivan_Bogyn._Tom_2_1407860765.txt',
# '/Users/mac/Datasets/ukrainian/texts/Ivan_Bohun.txt',
# '/Users/mac/Datasets/ukrainian/texts/Ivan_Kotlyarevskii_smiyetsya_1391268934.txt',
# '/Users/mac/Datasets/ukrainian/texts/Ivan_Mazepa.txt',
# '/Users/mac/Datasets/ukrainian/texts/Ivan_Mazepa1.txt',
# '/Users/mac/Datasets/ukrainian/texts/Ivan_Vyhovskyi.txt',
# '/Users/mac/Datasets/ukrainian/texts/Kaidany_dlia_oligarha.txt',
# '/Users/mac/Datasets/ukrainian/texts/Kalle_Bliumkvist_i_Rasmus.txt',
# '/Users/mac/Datasets/ukrainian/texts/Kapitan_dalekoho_plavannia.txt',
# '/Users/mac/Datasets/ukrainian/texts/Kinec-Velykoho-Yuliusa-Tetyana-Sytina.txt',
# '/Users/mac/Datasets/ukrainian/texts/KymitakymkiAnekdotidavniisychasni_1424966416.txt',
# '/Users/mac/Datasets/ukrainian/texts/LembergLwwLvivFatalnemisto_1413217253.txt',
# '/Users/mac/Datasets/ukrainian/texts/Miicholovikpingvin_1423069473.txt',
# '/Users/mac/Datasets/ukrainian/texts/Na_dvoh_tribynah._Opovidannya_ta_feiletoni_1374783116.txt',
# '/Users/mac/Datasets/ukrainian/texts/Pokhvala_Hlupoti.txt',
# '/Users/mac/Datasets/ukrainian/texts/Rangers._75-i_polk_reindjeriv_armij_SShA_1376161965.txt',
# '/Users/mac/Datasets/ukrainian/texts/Shodennik_nacionalnogo_geroya_Selepka_Lavochki_1380310831.txt',
# '/Users/mac/Datasets/ukrainian/texts/Troyevodnomychovniyakshonerahyvatisobaki_1413470797.txt',
# '/Users/mac/Datasets/ukrainian/texts/V-pastci-Karen-Libo.txt',
# '/Users/mac/Datasets/ukrainian/texts/V-pohoni-za-Pryvydom-Mykola-Toman.txt',
# '/Users/mac/Datasets/ukrainian/texts/V_ryadah_YPA_1375095172.txt',
# '/Users/mac/Datasets/ukrainian/texts/Vbyvstvo-na-31-mu-poversi-Per-Valee.txt',
# '/Users/mac/Datasets/ukrainian/texts/Vbyvtsi_na_bortu_zbirka.txt',
# '/Users/mac/Datasets/ukrainian/texts/Vid_Malorosii_do_Ukrainy.txt',
# '/Users/mac/Datasets/ukrainian/texts/Viklik_1369664950.txt',
# '/Users/mac/Datasets/ukrainian/texts/VishneviysmishkiZaboronenitvori_1416243642.txt',
# '/Users/mac/Datasets/ukrainian/texts/Vtrachenii_simvol_1371139594.txt',
# '/Users/mac/Datasets/ukrainian/texts/Vtrata_1459632673.txt',
# '/Users/mac/Datasets/ukrainian/texts/Ya_Pashtyet_i_Armiya_1372368122.txt',
# '/Users/mac/Datasets/ukrainian/texts/Yevpraksia.txt',
# '/Users/mac/Datasets/ukrainian/texts/Zabyte_vbivstvo_1371139744.txt',
# '/Users/mac/Datasets/ukrainian/texts/Zavisa.txt',
# '/Users/mac/Datasets/ukrainian/texts/Zdibniiychen_1425046188.txt',
# '/Users/mac/Datasets/ukrainian/texts/Zglyansyapomrizamistmene_1426068509.txt',
# '/Users/mac/Datasets/ukrainian/texts/Zolota-chetvirka-Devyatnadcyatyj-kilometr-Eduard-Fikker.txt',
# '/Users/mac/Datasets/ukrainian/texts/Zrada_1370256093.txt',
# '/Users/mac/Datasets/ukrainian/texts/Zviri.txt'],
#                '/Users/mac/Datasets/ukrainian/texts/text_plane')