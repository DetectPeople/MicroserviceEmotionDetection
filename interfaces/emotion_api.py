from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory

from entities import Emotion, Frame,Person,db
from repository.video_repository import VideoRepository
from repository.frame_repository import FrameRepository
from use_cases.process_emotion_use_case import ProcessEmotionUseCase

from config import Config
import os
import logging
import requests
from flask import Response
import csv
from io import StringIO

from collections import defaultdict
import statistics
import xlsxwriter
from io import BytesIO

emotion_api = Blueprint('emotion_api', __name__)
video_repository = VideoRepository()
frame_repository = FrameRepository()
process_emotion_use_case = ProcessEmotionUseCase()

@emotion_api.route('/', methods=['GET'])
def select_video():
    logging.info("Loaded video selection page.")
    videos = video_repository.get_all()
    return render_template('select_video.html', videos=videos)

@emotion_api.route('/process', methods=['POST'])
def process_video():
    video_id = int(request.form['video_id'])
    logging.info(f"Processing initiated for video ID {video_id}")

    # Redirect immediately to processing page
    return redirect(url_for('emotion_api.processing', video_id=video_id))

@emotion_api.route('/start_processing/<int:video_id>', methods=['GET'])
def start_processing(video_id):
    try:
        # Intentar procesar el video
        result = process_emotion_use_case.execute(video_id)

        # Si los frames no están listos, redirigir a frame_processing.html
        if result is None:
            logging.info(f"Frames for video ID {video_id} are still being processed.")
            return render_template('frame_processing.html', video_id=video_id)

        # Proceder al resultado si el procesamiento está completo
        output_video_filename = os.path.basename(result)
        logging.info(f"Emotion detection complete for video ID {video_id}")
        # Redirigir incluyendo ambos parámetros: video_filename y video_id
        return redirect(url_for('emotion_api.result', video_filename=output_video_filename, video_id=video_id))

    except Exception as e:
        logging.error(f"Error in processing video ID {video_id}: {e}")
        return f"Error processing video: {str(e)}", 500


@emotion_api.route('/processing/<int:video_id>')
def processing(video_id):
    # Render the processing page and then call the start processing endpoint
    return render_template('processing.html', video_id=video_id)

@emotion_api.route('/result/<video_filename>/<int:video_id>')
def result(video_filename, video_id):
    # Pasar el video_id al contexto de la plantilla
    return render_template('result.html', video_filename=video_filename, video_id=video_id)

@emotion_api.route('/videos/<video_filename>')
def get_video(video_filename):
    return send_from_directory(Config.ANNOTATED_VIDEOS_DIR, video_filename)


from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, Response
from entities import Emotion, Frame, db
from repository.video_repository import VideoRepository
from repository.frame_repository import FrameRepository
from use_cases.process_emotion_use_case import ProcessEmotionUseCase
from config import Config
import os
import logging
from collections import defaultdict
import statistics
import xlsxwriter
from io import BytesIO

emotion_api = Blueprint('emotion_api', __name__)
video_repository = VideoRepository()
frame_repository = FrameRepository()
process_emotion_use_case = ProcessEmotionUseCase()


@emotion_api.route('/', methods=['GET'])
def select_video():
    logging.info("Loaded video selection page.")
    videos = video_repository.get_all()
    return render_template('select_video.html', videos=videos)


@emotion_api.route('/process', methods=['POST'])
def process_video():
    video_id = int(request.form['video_id'])
    logging.info(f"Processing initiated for video ID {video_id}")
    return redirect(url_for('emotion_api.processing', video_id=video_id))


@emotion_api.route('/start_processing/<int:video_id>', methods=['GET'])
def start_processing(video_id):
    try:
        result = process_emotion_use_case.execute(video_id)
        if result is None:
            logging.info(f"Frames for video ID {video_id} are still being processed.")
            return render_template('frame_processing.html', video_id=video_id)

        output_video_filename = os.path.basename(result)
        logging.info(f"Emotion detection complete for video ID {video_id}")
        return redirect(url_for('emotion_api.result', video_filename=output_video_filename, video_id=video_id))
    except Exception as e:
        logging.error(f"Error in processing video ID {video_id}: {e}")
        return f"Error processing video: {str(e)}", 500


@emotion_api.route('/processing/<int:video_id>')
def processing(video_id):
    return render_template('processing.html', video_id=video_id)


@emotion_api.route('/result/<video_filename>/<int:video_id>')
def result(video_filename, video_id):
    return render_template('result.html', video_filename=video_filename, video_id=video_id)


@emotion_api.route('/videos/<video_filename>')
def get_video(video_filename):
    return send_from_directory(Config.ANNOTATED_VIDEOS_DIR, video_filename)


from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, Response
from entities import Emotion, Frame, db
from repository.video_repository import VideoRepository
from repository.frame_repository import FrameRepository
from use_cases.process_emotion_use_case import ProcessEmotionUseCase
from config import Config
import os
import logging
from collections import defaultdict
import statistics
import xlsxwriter
from io import BytesIO

emotion_api = Blueprint('emotion_api', __name__)
video_repository = VideoRepository()
frame_repository = FrameRepository()
process_emotion_use_case = ProcessEmotionUseCase()

@emotion_api.route('/', methods=['GET'])
def select_video():
    logging.info("Loaded video selection page.")
    videos = video_repository.get_all()
    return render_template('select_video.html', videos=videos)

@emotion_api.route('/process', methods=['POST'])
def process_video():
    video_id = int(request.form['video_id'])
    logging.info(f"Processing initiated for video ID {video_id}")
    return redirect(url_for('emotion_api.processing', video_id=video_id))

@emotion_api.route('/start_processing/<int:video_id>', methods=['GET'])
def start_processing(video_id):
    try:
        result = process_emotion_use_case.execute(video_id)
        if result is None:
            logging.info(f"Frames for video ID {video_id} are still being processed.")
            return render_template('frame_processing.html', video_id=video_id)

        output_video_filename = os.path.basename(result)
        logging.info(f"Emotion detection complete for video ID {video_id}")
        return redirect(url_for('emotion_api.result', video_filename=output_video_filename, video_id=video_id))
    except Exception as e:
        logging.error(f"Error in processing video ID {video_id}: {e}")
        return f"Error processing video: {str(e)}", 500

@emotion_api.route('/processing/<int:video_id>')
def processing(video_id):
    return render_template('processing.html', video_id=video_id)

@emotion_api.route('/result/<video_filename>/<int:video_id>')
def result(video_filename, video_id):
    return render_template('result.html', video_filename=video_filename, video_id=video_id)

@emotion_api.route('/videos/<video_filename>')
def get_video(video_filename):
    return send_from_directory(Config.ANNOTATED_VIDEOS_DIR, video_filename)

from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, Response
from entities import Emotion, Frame, db
from repository.video_repository import VideoRepository
from repository.frame_repository import FrameRepository
from use_cases.process_emotion_use_case import ProcessEmotionUseCase
from config import Config
import os
import logging
from collections import defaultdict
import statistics
import xlsxwriter
from io import BytesIO

emotion_api = Blueprint('emotion_api', __name__)
video_repository = VideoRepository()
frame_repository = FrameRepository()
process_emotion_use_case = ProcessEmotionUseCase()

@emotion_api.route('/', methods=['GET'])
def select_video():
    logging.info("Loaded video selection page.")
    videos = video_repository.get_all()
    return render_template('select_video.html', videos=videos)

@emotion_api.route('/process', methods=['POST'])
def process_video():
    video_id = int(request.form['video_id'])
    logging.info(f"Processing initiated for video ID {video_id}")
    return redirect(url_for('emotion_api.processing', video_id=video_id))

@emotion_api.route('/start_processing/<int:video_id>', methods=['GET'])
def start_processing(video_id):
    try:
        result = process_emotion_use_case.execute(video_id)
        if result is None:
            logging.info(f"Frames for video ID {video_id} are still being processed.")
            return render_template('frame_processing.html', video_id=video_id)

        output_video_filename = os.path.basename(result)
        logging.info(f"Emotion detection complete for video ID {video_id}")
        return redirect(url_for('emotion_api.result', video_filename=output_video_filename, video_id=video_id))
    except Exception as e:
        logging.error(f"Error in processing video ID {video_id}: {e}")
        return f"Error processing video: {str(e)}", 500

@emotion_api.route('/processing/<int:video_id>')
def processing(video_id):
    return render_template('processing.html', video_id=video_id)

@emotion_api.route('/result/<video_filename>/<int:video_id>')
def result(video_filename, video_id):
    return render_template('result.html', video_filename=video_filename, video_id=video_id)

@emotion_api.route('/videos/<video_filename>')
def get_video(video_filename):
    return send_from_directory(Config.ANNOTATED_VIDEOS_DIR, video_filename)

@emotion_api.route('/download_emotions_excel/<int:video_id>', methods=['GET'])
def download_emotions_excel(video_id):
    try:
        # Hacer una consulta directa para obtener todos los datos relevantes de Frame y Emotion para un video específico
        results = (
            db.session.query(Frame.id, Frame.frame_number, Frame.video_id, Frame.average_brightness,
                             Frame.contrast_ratio, Frame.background_complexity, Frame.color_temperature,
                             Frame.sharpness, Emotion.emotion_type, Emotion.confidence, Emotion.bbox,
                             Emotion.person_identity, Emotion.person_id)
            .join(Emotion, Frame.id == Emotion.frame_id)
            .filter(Frame.video_id == video_id)
            .all()
        )

        # Obtener las estimaciones de edad y género de todas las personas detectadas en el video
        person_info = (
            db.session.query(Person.id, Person.identity, Person.age_estimation, Person.gender_estimation)
            .join(Emotion, Person.id == Emotion.person_id)
            .join(Frame, Frame.id == Emotion.frame_id)
            .filter(Frame.video_id == video_id)
            .distinct()
            .all()
        )

        # Verificar si hay resultados
        if not results:
            logging.error(f"No data found for video ID {video_id}")
            return f"No emotion data found for video ID {video_id}", 404

        # Crear un archivo Excel en memoria
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Emotion Data')

        # Escribir el encabezado del Excel, incluyendo las nuevas columnas
        headers = ['Frame ID', 'Frame Number in Video', 'Video ID', 'Average Brightness', 'Contrast Ratio',
                   'Background Complexity', 'Color Temperature', 'Sharpness', 'Detected Emotion',
                   'Confidence Level (%)', 'Bounding Box Coordinates', 'Person Identity', 'Person ID']
        worksheet.write_row('A1', headers)

        # Variables para métricas
        total_confidence = []
        emotion_count = defaultdict(int)
        person_emotion_count = defaultdict(int)  # Contador de emociones por persona

        # Listas para calcular los promedios de las métricas de frame
        brightness_values = []
        contrast_values = []
        complexity_values = []
        temperature_values = []
        sharpness_values = []

        # Escribir los datos en el Excel y acumular métricas
        row_index = 1
        for row in results:
            (frame_id, frame_number, video_id, average_brightness, contrast_ratio, background_complexity,
             color_temperature, sharpness, emotion_type, confidence, bbox, person_identity, person_id) = row

            # Guardar la información en la hoja de Excel
            worksheet.write_row(row_index, 0, [
                frame_id,  # Frame ID
                frame_number,  # Frame Number
                video_id,  # Video ID
                average_brightness if average_brightness is not None else 'N/A',  # Average Brightness
                contrast_ratio if contrast_ratio is not None else 'N/A',  # Contrast Ratio
                background_complexity if background_complexity is not None else 'N/A',  # Background Complexity
                color_temperature if color_temperature is not None else 'N/A',  # Color Temperature
                sharpness if sharpness is not None else 'N/A',  # Sharpness
                emotion_type,  # Detected Emotion
                round(confidence * 100, 2),  # Confidence Level as Percentage
                bbox,  # Bounding Box
                person_identity if person_identity else 'Unknown',  # Person Identity
                person_id  # Person ID
            ])

            # Acumular datos para métricas
            if average_brightness is not None:
                brightness_values.append(average_brightness)
            if contrast_ratio is not None:
                contrast_values.append(contrast_ratio)
            if background_complexity is not None:
                complexity_values.append(background_complexity)
            if color_temperature is not None:
                temperature_values.append(color_temperature)
            if sharpness is not None:
                sharpness_values.append(sharpness)
            total_confidence.append(confidence)
            emotion_count[emotion_type] += 1
            person_emotion_count[person_id] += 1
            row_index += 1

        # Calcular promedios de las métricas de frame
        avg_brightness = round(statistics.mean(brightness_values), 2) if brightness_values else 0
        avg_contrast = round(statistics.mean(contrast_values), 2) if contrast_values else 0
        avg_complexity = round(statistics.mean(complexity_values), 2) if complexity_values else 0
        avg_temperature = round(statistics.mean(temperature_values), 2) if temperature_values else 0
        avg_sharpness = round(statistics.mean(sharpness_values), 2) if sharpness_values else 0

        # Calcular métricas de emociones
        avg_confidence = round(statistics.mean(total_confidence) * 100, 2) if total_confidence else 0
        most_common_emotion = max(emotion_count, key=emotion_count.get) if emotion_count else "None"
        avg_emotions_per_person = round(sum(person_emotion_count.values()) / len(person_emotion_count),
                                        2) if person_emotion_count else 0

        # Escribir resumen de métricas
        summary_start_row = row_index + 2
        worksheet.write(summary_start_row, 0, 'Summary:')
        worksheet.write(summary_start_row + 1, 0, 'Total Frames Analyzed')
        worksheet.write(summary_start_row + 1, 1, len(set([row[0] for row in results])))
        worksheet.write(summary_start_row + 2, 0, 'Total Emotions Detected')
        worksheet.write(summary_start_row + 2, 1, len(results))
        worksheet.write(summary_start_row + 3, 0, 'Average Confidence Level (%)')
        worksheet.write(summary_start_row + 3, 1, avg_confidence)
        worksheet.write(summary_start_row + 4, 0, 'Most Common Emotion Detected')
        worksheet.write(summary_start_row + 4, 1, most_common_emotion)
        worksheet.write(summary_start_row + 5, 0, 'Average Number of Emotions per Person')
        worksheet.write(summary_start_row + 5, 1, avg_emotions_per_person)

        # Escribir promedios de las métricas de frame
        worksheet.write(summary_start_row + 7, 0, 'Frame Metrics:')
        worksheet.write(summary_start_row + 8, 0, 'Average Brightness')
        worksheet.write(summary_start_row + 8, 1, avg_brightness)
        worksheet.write(summary_start_row + 9, 0, 'Average Contrast Ratio')
        worksheet.write(summary_start_row + 9, 1, avg_contrast)
        worksheet.write(summary_start_row + 10, 0, 'Average Background Complexity')
        worksheet.write(summary_start_row + 10, 1, avg_complexity)
        worksheet.write(summary_start_row + 11, 0, 'Average Color Temperature')
        worksheet.write(summary_start_row + 11, 1, avg_temperature)
        worksheet.write(summary_start_row + 12, 0, 'Average Sharpness')
        worksheet.write(summary_start_row + 12, 1, avg_sharpness)

        # Escribir información de todas las personas detectadas
        person_info_start_row = summary_start_row + 14
        worksheet.write(person_info_start_row, 0, 'Detected Persons:')
        worksheet.write_row(person_info_start_row + 1, 0, ['Person ID', 'Identity', 'Age Estimation', 'Gender Estimation'])

        # Escribir cada persona detectada en el Excel
        for index, person in enumerate(person_info):
            worksheet.write_row(person_info_start_row + 2 + index, 0, [
                person.id,  # Person ID
                person.identity if person.identity else 'Unknown',  # Identity
                person.age_estimation if person.age_estimation else 'Unknown',  # Age Estimation
                person.gender_estimation if person.gender_estimation else 'Unknown'  # Gender Estimation
            ])

        # Crear gráficos para visualización

        # 1. Gráfico de Frecuencia de Emociones
        emotion_chart = workbook.add_chart({'type': 'column'})
        emotion_names = list(emotion_count.keys())
        emotion_values = list(emotion_count.values())

        # Escribir los nombres de emociones y sus frecuencias para el gráfico
        chart_data_row = person_info_start_row + len(person_info) + 4
        worksheet.write_row(chart_data_row, 0, ['Emotion', 'Frequency'])
        for i, (emotion, count) in enumerate(emotion_count.items()):
            worksheet.write(chart_data_row + i + 1, 0, emotion)
            worksheet.write(chart_data_row + i + 1, 1, count)

        # Configurar datos del gráfico de emociones
        emotion_chart.add_series({
            'categories': f'={worksheet.name}!$A${chart_data_row + 2}:$A${chart_data_row + len(emotion_count) + 1}',
            'values': f'={worksheet.name}!$B${chart_data_row + 2}:$B${chart_data_row + len(emotion_count) + 1}',
            'name': 'Emotion Frequency'
        })

        emotion_chart.set_title({'name': 'Emotion Frequency Analysis'})
        emotion_chart.set_x_axis({'name': 'Emotion'})
        emotion_chart.set_y_axis({'name': 'Frequency'})
        emotion_chart.set_style(11)

        # Insertar el gráfico de emociones en la hoja de Excel
        worksheet.insert_chart(f'A{chart_data_row + len(emotion_count) + 4}', emotion_chart)

        # 2. Gráfico de promedios de las métricas de frame
        avg_chart = workbook.add_chart({'type': 'bar'})
        metric_names = ['Average Brightness', 'Contrast Ratio', 'Background Complexity', 'Color Temperature', 'Sharpness']
        metric_values = [avg_brightness, avg_contrast, avg_complexity, avg_temperature, avg_sharpness]

        # Escribir nombres de métricas y sus promedios para el gráfico
        metric_chart_data_row = chart_data_row + len(emotion_count) + 6
        worksheet.write_row(metric_chart_data_row, 0, ['Metric', 'Average Value'])
        for i, (metric, value) in enumerate(zip(metric_names, metric_values)):
            worksheet.write(metric_chart_data_row + i + 1, 0, metric)
            worksheet.write(metric_chart_data_row + i + 1, 1, value)

        # Configurar datos del gráfico de métricas
        avg_chart.add_series({
            'categories': f'={worksheet.name}!$A${metric_chart_data_row + 2}:$A${metric_chart_data_row + len(metric_names) + 1}',
            'values': f'={worksheet.name}!$B${metric_chart_data_row + 2}:$B${metric_chart_data_row + len(metric_names) + 1}',
            'name': 'Average Metrics'
        })

        avg_chart.set_title({'name': 'Frame Metrics Analysis'})
        avg_chart.set_x_axis({'name': 'Metric'})
        avg_chart.set_y_axis({'name': 'Average Value'})
        avg_chart.set_style(11)

        # Insertar el gráfico de métricas en la hoja de Excel
        worksheet.insert_chart(f'A{metric_chart_data_row + len(metric_names) + 4}', avg_chart)

        # Cerrar y devolver el archivo Excel
        workbook.close()
        output.seek(0)

        return Response(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": f"attachment;filename=emotion_data_report_for_video_{video_id}.xlsx"}
        )

    except Exception as e:
        logging.error(f"Error generating Excel for video ID {video_id}: {str(e)}")
        return f"Error generating Excel for video ID {video_id}: {str(e)}", 500
