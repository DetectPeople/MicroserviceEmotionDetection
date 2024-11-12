from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory

from entities import Emotion, Frame, db
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
    """Endpoint to start processing after rendering the processing page."""
    try:
        # Attempt to process the video
        result = process_emotion_use_case.execute(video_id)

        # If frames are not ready, redirect to frame_processing.html
        if result is None:
            logging.info(f"Frames for video ID {video_id} are still being processed.")
            return render_template('frame_processing.html', video_id=video_id)

        # Proceed to result if processing is complete
        output_video_filename = os.path.basename(result)
        logging.info(f"Emotion detection complete for video ID {video_id}")
        return redirect(url_for('emotion_api.result', video_filename=output_video_filename))

    except Exception as e:
        logging.error(f"Error in processing video ID {video_id}: {e}")
        return f"Error processing video: {str(e)}", 500


@emotion_api.route('/processing/<int:video_id>')
def processing(video_id):
    # Render the processing page and then call the start processing endpoint
    return render_template('processing.html', video_id=video_id)

@emotion_api.route('/result/<video_filename>')
def result(video_filename):
    return render_template('result.html', video_filename=video_filename)

@emotion_api.route('/videos/<video_filename>')
def get_video(video_filename):
    return send_from_directory(Config.ANNOTATED_VIDEOS_DIR, video_filename)


@emotion_api.route('/download_emotions_excel', methods=['GET'])
def download_emotions_excel():
    try:
        # Hacer una consulta directa para obtener todos los datos relevantes de Frame y Emotion
        results = (
            db.session.query(Frame.id, Frame.frame_number, Frame.video_id, Emotion.emotion_type,
                             Emotion.confidence, Emotion.bbox, Emotion.person_identity, Emotion.person_id)
            .join(Emotion, Frame.id == Emotion.frame_id)
            .all()
        )

        # Verificar si hay resultados
        if not results:
            logging.error("No data found in frame repository")
            return "No emotion data found", 404

        # Crear un archivo Excel en memoria
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Emotion Data')

        # Escribir el encabezado del Excel, incluyendo person_id
        headers = ['Frame ID', 'Frame Number in Video', 'Video ID', 'Detected Emotion', 'Confidence Level (%)',
                   'Bounding Box Coordinates', 'Person Identity', 'Person ID']
        worksheet.write_row('A1', headers)

        # Variables para métricas
        total_confidence = []
        emotion_count = defaultdict(int)
        video_emotion_count = defaultdict(int)
        person_emotion_count = defaultdict(int)  # Contador de emociones por persona

        # Escribir los datos en el Excel y acumular métricas
        row_index = 1
        for row in results:
            frame_id, frame_number, video_id, emotion_type, confidence, bbox, person_identity, person_id = row

            # Guardar información en la hoja de Excel
            worksheet.write_row(row_index, 0, [
                frame_id,  # Frame ID
                frame_number,  # Frame Number
                video_id,  # Video ID
                emotion_type,  # Detected Emotion
                round(confidence * 100, 2),  # Confidence Level as Percentage
                bbox,  # Bounding Box
                person_identity if person_identity else 'Unknown',  # Person Identity
                person_id  # Person ID
            ])

            # Acumular datos para métricas
            total_confidence.append(confidence)
            emotion_count[emotion_type] += 1
            video_emotion_count[video_id] += 1
            person_emotion_count[person_id] += 1
            row_index += 1

        # Calcular métricas
        avg_confidence = round(statistics.mean(total_confidence) * 100, 2) if total_confidence else 0
        most_common_emotion = max(emotion_count, key=emotion_count.get) if emotion_count else "None"
        avg_emotions_per_video = round(sum(video_emotion_count.values()) / len(video_emotion_count),
                                       2) if video_emotion_count else 0
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
        worksheet.write(summary_start_row + 5, 0, 'Average Number of Emotions per Video')
        worksheet.write(summary_start_row + 5, 1, avg_emotions_per_video)
        worksheet.write(summary_start_row + 6, 0, 'Average Number of Emotions per Person')
        worksheet.write(summary_start_row + 6, 1, avg_emotions_per_person)

        # Agregar gráficos para una mejor comprensión visual

        # 1. Gráfico de Frecuencia de Emociones
        chart = workbook.add_chart({'type': 'column'})
        emotion_names = list(emotion_count.keys())
        emotion_values = list(emotion_count.values())

        # Escribir los nombres de emociones y sus frecuencias para el gráfico
        chart_data_row = summary_start_row + 8
        worksheet.write_row(chart_data_row, 0, ['Emotion', 'Frequency'])
        for i, (emotion, count) in enumerate(emotion_count.items()):
            worksheet.write(chart_data_row + i + 1, 0, emotion)
            worksheet.write(chart_data_row + i + 1, 1, count)

        # Configurar datos del gráfico
        chart.add_series({
            'categories': f'={worksheet.name}!$A${chart_data_row + 2}:$A${chart_data_row + len(emotion_count) + 1}',
            'values': f'={worksheet.name}!$B${chart_data_row + 2}:$B${chart_data_row + len(emotion_count) + 1}',
            'name': 'Emotion Frequency'
        })

        chart.set_title({'name': 'Emotion Frequency Analysis'})
        chart.set_x_axis({'name': 'Emotion'})
        chart.set_y_axis({'name': 'Frequency'})
        chart.set_style(11)

        # Insertar el gráfico en la hoja de Excel
        worksheet.insert_chart(f'A{chart_data_row + len(emotion_count) + 4}', chart)

        # Cerrar y devolver el archivo Excel
        workbook.close()
        output.seek(0)

        return Response(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": "attachment;filename=emotion_data_report.xlsx"}
        )

    except Exception as e:
        logging.error(f"Error generating Excel: {str(e)}")
        return f"Error generating Excel: {str(e)}", 500
