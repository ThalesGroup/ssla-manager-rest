{{- define "ssla-manager.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "ssla-manager.labels" -}}
helm.sh/chart: {{ include "ssla-manager.chart" . }}
{{ include "ssla-manager.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "ssla-manager.selectorLabels" -}}
{{- printf "app.kubernetes.io/name: %s-ssla-manager" .Release.Name | trunc 63 | trimSuffix "-" }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
