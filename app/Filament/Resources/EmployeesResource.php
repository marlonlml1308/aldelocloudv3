<?php

namespace App\Filament\Resources;

use App\Filament\Resources\EmployeesResource\Pages;
use App\Filament\Resources\EmployeesResource\RelationManagers;
use App\Models\Employees;
use Filament\Forms;
use Filament\Forms\Components\Section;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Form;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletingScope;
use pxlrbt\FilamentExcel\Actions\Tables\ExportBulkAction;
use Illuminate\Support\Facades\DB;

class EmployeesResource extends Resource
{
    protected static ?string $model = Employees::class;
    protected static ?string $navigationGroup = 'Empleados';
    protected static ?string $navigationIcon = 'heroicon-o-users';

    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\TextInput::make('firstname')->label('Nombre')
                ->required()
                ->maxLength(15),
                Forms\Components\TextInput::make('lastname')->label('Apellido')
                ->required()
                ->maxLength(15),
                Forms\Components\Grid::make(3)
                ->schema([
                Forms\Components\Select::make('jobtitleid')->label('Cargo')
                ->required()
                ->relationship('jobtitles', 'jobtitletext', function ($query) {
                    $query->where('jobtitleinactive', '!=', true);
                }),
                Forms\Components\Select::make('securitylevel')->label('Nivel de Seguridad')
                ->required()
                ->options([
                    '1' => '1',
                    '2' => '2',
                    '3' => '3',
                    '4' => '4',
                    '5' => '5',
                ]),
                Forms\Components\Toggle::make('employeeinactive')
                ->label('Inactivo')
                ->required()
                ->inline(false)
                ->reactive() // Detecta cambios en el toggle
                ->afterStateUpdated(fn ($state, Forms\Set $set) => $set('accesscode', $state ? null : '')), // Setea NULL si está activo
                ]),
                TextInput::make('socialsecuritynumber')
                ->label('Numero de Documento')
                ->required()
                ->numeric()
                ->maxLength(15)
                ->rule(function (string $operation, ?Model $record = null) {
                    return function ($attribute, $value, $fail) use ($operation, $record) {
                        if ($value !== null) {
                            $query = DB::table('employeefiles')
                                ->where('socialsecuritynumber', $value);
                            if ($operation === 'edit' && $record) {
                                $query->where('id', '!=', $record->id);
                            }
                            $exists = $query->exists();
                            if ($exists) {
                                $fail('El documento ya está en uso');
                            }
                        }
                    };
                }),
                Forms\Components\TextInput::make('accesscode')
                ->label('Codigo')
                ->nullable() // Permite valores NULL
                ->numeric()
                ->maxLength(8)
                ->rule(function (string $operation, ?Model $record = null) {
                    return function ($attribute, $value, $fail) use ($operation, $record) {
                        if ($value !== null) {
                            $query = DB::table('employeefiles')
                                ->where('accesscode', $value);
                            if ($operation === 'edit' && $record) {
                                $query->where('id', '!=', $record->id);
                            }
                            $exists = $query->exists();
                            if ($exists) {
                                $fail('El codigo ya está en uso');
                            }
                        }
                    };
                }),
            ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            //->paginated(false)
            ->columns([
                //
                Tables\Columns\TextColumn::make('firstname')->label('Nombre')
                ->sortable()
                ->searchable(),
                Tables\Columns\TextColumn::make('lastname')->label('Apellido')
                ->sortable()
                ->searchable(),
                Tables\Columns\TextColumn::make('jobtitles.jobtitletext')->label('Cargo')
                ->sortable(),
                Tables\Columns\TextColumn::make('securitylevel')->label('Nivel de Seguridad'),
                Tables\Columns\TextColumn::make('accesscode')->label('Codigo'),
                Tables\Columns\CheckboxColumn::make('employeeinactive')->label('Inactivo')
                ->disabled()
                ->sortable(),
            ])
            ->filters([
                //
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
            ])
            ->bulkActions([
                // Tables\Actions\BulkActionGroup::make([
                    // Tables\Actions\DeleteBulkAction::make(),
                    ExportBulkAction::make(),
                // ]),
            ]);
    }

    public static function getRelations(): array
    {
        return [
            //
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListEmployees::route('/'),
            'create' => Pages\CreateEmployees::route('/create'),
            'edit' => Pages\EditEmployees::route('/{record}/edit'),
        ];
    }
    public static function getModelLabel(): string
    {
        return __(key: 'Empleado');
    }
    public static function getPluralModelLabel(): string
    {
        return __(key: 'Empleados');
    }
}
