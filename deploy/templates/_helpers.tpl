{{/*
Expand the name of the chart.
*/}}
{{- define "alioth.name" -}}
{{- default .Chart.Name .Values.alioth.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "alioth.fullname" -}}
{{- if .Values.alioth.fullnameOverride }}
{{- .Values.alioth.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.alioth.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "alioth.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "alioth.labels" -}}
helm.sh/chart: {{ include "alioth.chart" . }}
{{ include "alioth.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "alioth.selectorLabels" -}}
app.kubernetes.io/name: {{ include "alioth.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "alioth.serviceAccountName" -}}
{{- if .Values.alioth.serviceAccount.create }}
{{- default (include "alioth.fullname" .) .Values.alioth.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.alioth.serviceAccount.name }}
{{- end }}
{{- end }}
